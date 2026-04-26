import os
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TQDM_DISABLE", "1")

from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from transformers.utils import logging as transformers_logging
from huggingface_hub.utils import close_session, disable_progress_bars

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
disable_progress_bars()
transformers_logging.disable_progress_bar()

try:
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    print("Loading config...")
    config = AutoConfig.from_pretrained(MODEL)
    print("Loading model...")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
    close_session()