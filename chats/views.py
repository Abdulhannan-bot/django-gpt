from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import ChatBody, OpenAICompletion, OpenAIMessage
from .services import ChatService

@api_view(['POST'])
def chat_completion(request):
    body_data = request.data
    chat_body = ChatBody.objects.create(
        use_context=body_data.get('use_context', False),
        include_sources=body_data.get('include_sources', True),
        stream=body_data.get('stream', False)
    )
    messages_data = body_data.get('messages', [])
    for message_data in messages_data:
        message = OpenAIMessage.objects.create(
            role=message_data['role'],
            content=message_data['content']
        )
        chat_body.messages.add(message)
    
    service = ChatService()  # Instantiate your service
    completion = service.chat(
        messages=chat_body.messages.all(),
        use_context=chat_body.use_context,
        # Pass other parameters as needed
    )
    
    response_data = {
        "id": completion.id,
        "object": completion.object,
        "created": completion.created,
        "model": completion.model,
        # Add more fields as needed
    }
    
    return Response(response_data, status=status.HTTP_200_OK)