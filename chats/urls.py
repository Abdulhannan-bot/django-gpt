from django.utils import path
from . import views

urlpattersn = [
    path('chat/completions', views.chat_completion, name="chat_completions")
]