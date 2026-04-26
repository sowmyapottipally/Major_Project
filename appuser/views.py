from django.shortcuts import render
from accounts.models import RegUser
import os
import sys
import re
from pathlib import Path

# Force Transformers / Torch to CPU-only mode in non-GPU environment
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TRANSFORMERS_NO_CUDA", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("TRANSFORMERS_NO_CUDA", "1")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
# Optional local cache dir (avoid repeats and network issues)
cache_root = Path(__file__).resolve().parent.parent / "hf_cache"
os.environ.setdefault("HF_HOME", str(cache_root))

import torch

# Ensure tqdm writes to stdout (WSGI environments may have limited stderr support on Windows)
try:
    import tqdm
    _orig_tqdm = getattr(tqdm, 'tqdm', None)
    if _orig_tqdm is not None:
        def _tqdm_safe(*args, **kwargs):
            kwargs['disable'] = True
            if 'file' not in kwargs:
                kwargs['file'] = sys.stdout
            return _orig_tqdm(*args, **kwargs)
        tqdm.tqdm = _tqdm_safe
except Exception:
    pass

from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from transformers.utils import logging as transformers_logging
from huggingface_hub.utils import close_session, disable_progress_bars
import numpy as np
from scipy.special import softmax


def userhome(request):
    return render(request, 'appuser/home.html')


def train_sentiment_model(request):
    return render(request, 'appuser/modeltrain.html')


MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = None
config = None
model = None
disable_progress_bars()
transformers_logging.disable_progress_bar()


def get_model_components():
    global tokenizer, config, model

    if tokenizer is None or config is None or model is None:
        last_exc = None
        for _ in range(2):
            try:
                tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=False)
                config = AutoConfig.from_pretrained(MODEL, local_files_only=False)
                model = AutoModelForSequenceClassification.from_pretrained(MODEL, local_files_only=False)
                model = model.to('cpu')
                break
            except Exception as exc:
                last_exc = exc
                close_session()
                disable_progress_bars()
                transformers_logging.disable_progress_bar()
        else:
            raise RuntimeError(f"Failed to initialize sentiment model: {last_exc}") from last_exc

    return tokenizer, config, model


POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "love", "liked", "like",
    "best", "wonderful", "fantastic", "superb", "enjoyed", "positive", "happy",
}
NEGATIVE_WORDS = {
    "bad", "worst", "awful", "terrible", "hate", "hated", "boring", "poor",
    "disappointing", "negative", "sad", "angry", "ugly", "stupid", "asshole",
}


def simple_lexicon_sentiment(text):
    tokens = re.findall(r"[A-Za-z']+", text.lower())
    if not tokens:
        return [
            {"label": "NEUTRAL", "score": 1.0},
            {"label": "POSITIVE", "score": 0.0},
            {"label": "NEGATIVE", "score": 0.0},
        ]

    pos_count = sum(1 for token in tokens if token in POSITIVE_WORDS)
    neg_count = sum(1 for token in tokens if token in NEGATIVE_WORDS)
    total = max(1, pos_count + neg_count)

    if pos_count == 0 and neg_count == 0:
        neutral, positive, negative = 0.8, 0.1, 0.1
    else:
        positive = pos_count / total
        negative = neg_count / total
        neutral = max(0.0, 1.0 - (positive + negative))

    predictions = [
        {"label": "POSITIVE", "score": round(float(positive), 4)},
        {"label": "NEGATIVE", "score": round(float(negative), 4)},
        {"label": "NEUTRAL", "score": round(float(neutral), 4)},
    ]
    predictions.sort(key=lambda item: item["score"], reverse=True)
    return predictions

# Preprocess text (replace usernames and links)
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

# Define a function to handle user input and make predictions
def sentiment_analysis(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()

        if not user_input:
            return render(
                request,
                'appuser/sentiment_form.html',
                {'error': 'Please enter text before analyzing sentiment.', 'user_input': user_input},
            )
        
        # Preprocess the input text
        processed_text = preprocess(user_input)
        
        model_warning = None
        try:
            # Tokenize and predict
            tokenizer_obj, config_obj, model_obj = get_model_components()
            encoded_input = tokenizer_obj(processed_text, return_tensors='pt')
            encoded_input = {k: v.cpu() for k, v in encoded_input.items()}
            model_obj = model_obj.to('cpu')
            with torch.no_grad():
                output = model_obj(**encoded_input)
            scores = output[0][0].detach().cpu().numpy()
            scores = softmax(scores)
            ranking = np.argsort(scores)[::-1]
            predictions = []
            for i in range(scores.shape[0]):
                label = config_obj.id2label[ranking[i]]
                score = round(float(scores[ranking[i]]), 4)
                predictions.append({"label": label, "score": score})
        except Exception as exc:
            model_warning = "Deep model is temporarily unavailable. Showing fallback sentiment result."
            predictions = simple_lexicon_sentiment(processed_text)

            # Debug: save exception for diagnosis
            print("Deep model error:", repr(exc))
            predictions = simple_lexicon_sentiment(processed_text)
            model_warning = (
                "Deep model is temporarily unavailable. Showing fallback sentiment result."
            )
        
        # Render results to the HTML template
        return render(
            request,
            'appuser/result.html',
            {'predictions': predictions, 'user_input': user_input, 'model_warning': model_warning},
        )
    
    return render(request, 'appuser/sentiment_form.html')
