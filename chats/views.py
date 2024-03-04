from django.shortcuts import render

# Create your views here.
from llama_index.llms import ChatMessage, MessageRole
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import ChatBody
from open_ai.models import (
    OpenAICompletion,
    OpenAIMessage,
    to_openai_response,
    to_openai_sse_stream,
)
from .services import ChatService
from starlette.responses import StreamingResponse

# @api_view(['POST'])
# def chat_completion(request):
#     body_data = request.data
#     chat_body = ChatBody.objects.create(
#         use_context=body_data.get('use_context', False),
#         include_sources=body_data.get('include_sources', True),
#         stream=body_data.get('stream', False)
#     )
#     messages_data = body_data.get('messages', [])
#     for message_data in messages_data:
#         message = OpenAIMessage.objects.create(
#             role=message_data['role'],
#             content=message_data['content']
#         )
#         chat_body.messages.add(message)
    
#     service = ChatService()  # Instantiate your service
#     all_messages = [
#         ChatMessage(content=m.content, role=MessageRole(m.role)) for m in body.messages
#     ]
#     completion = service.chat(
#         messages=chat_body.messages.all(),
#         use_context=chat_body.use_context,
#         # Pass other parameters as needed
#     )
    
#     response_data = {
#         "id": completion.id,
#         "object": completion.object,
#         "created": completion.created,
#         "model": completion.model,
#         # Add more fields as needed
#     }
    
#     return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def chat_completion(request):
    body_data = request.data
    print(body_data)
    service = ChatService()  # Instantiate your service
    all_messages = [
        ChatMessage(content=m.get("content"), role=MessageRole(m.get("role"))) for m in body_data.get("messages")
    ]
    if body_data.get("stream"):
        completion_gen = service.stream_chat(
            messages=all_messages,
            use_context=body_data.get("use_context"),
            context_filter=body_data.get("context_filter"),
        )

        return StreamingResponse(
            to_openai_sse_stream(
                completion_gen.response,
                completion_gen.sources if body_data.get("include_sources") else None,
            ),
            media_type="text/event-stream",
        )
    
    else:
        completion = service.chat(
            messages=all_messages,
            use_context=body_data.get("use_context"),
            context_filter=body_data.get("context_filter"),
        )
        return to_openai_response(
            completion.response, completion.sources if body_data.get("include_sources") else None
        )

    
    
    # completion = service.chat(
    #     messages=all_messages,
    #     use_context=body_data.get("use_context"),
    #     # Pass other parameters as needed
    # )
    
    # response_data = {
    #     #"id": completion.id,
    #     #"object": completion.object,
    #     #"created": completion.created,
    #     #"model": completion.model,
    #     "reponse":completion.response,
    #     # Add more fields as needed
    # }
    
    # return Response(response_data, status=status.HTTP_200_OK)
