from django.urls import path
from . import views
urlpatterns = [
    path('userhome/',views.userhome,name='userhome'),
    path('train/', views.train_sentiment_model, name='train_sentiment_model'),
    path('predict_sentiment/', views.sentiment_analysis, name='predict_sentiment'),
]