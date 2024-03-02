from django.urls import path
from . import views

urlpatterns = [
    path('chat/completions', views.chat_completion, name="chat_completions")
]