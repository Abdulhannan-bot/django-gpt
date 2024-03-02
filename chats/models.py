from django.db import models
from chunks.models import Chunk
from llama_index.types import TokenGen
from open_ai.models import ContextFilter, OpenAIMessage
# Create your models here.

class TokenGenField(models.TextField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return TokenGen(value)

    def to_python(self, value):
        if isinstance(value, TokenGen):
            return value
        if value is None:
            return None
        return TokenGen(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return str(value.data)
    

class Completion(models.Model):
    response = models.CharField(max_length=255, null = True, blank = True)
    sources = models.ManyToManyField(Chunk, null=True)

class CompletionGen(models.Model):
    response = TokenGenField()
    sources = models.ManyToManyField(Chunk, null=True, on_delete=models.CASCADE)

class ChatBody(models.Model):
    """Model representing chat body."""
    
    messages = models.ManyToManyField(OpenAIMessage, on_delete=models.CASCADE)
    use_context = models.BooleanField(default=False)
    context_filter = models.ForeignKey(ContextFilter, null=True, on_delete=models.SET_NULL)
    include_sources = models.BooleanField(default=True)
    stream = models.BooleanField(default=False)

    @classmethod
    def from_json(cls, json_data):
        chat_body = cls.objects.create(
            use_context=json_data.get('use_context', False),
            include_sources=json_data.get('include_sources', True),
            stream=json_data.get('stream', False)
        )
        
        # Create OpenAIMessage instances and add them to the chat body
        messages_data = json_data.get('messages', [])
        for message_data in messages_data:
            message = OpenAIMessage.objects.create(
                role=message_data['role'],
                content=message_data['content']
            )
            chat_body.messages.add(message)
        
        # Create ContextFilter instance if provided
        context_filter_data = json_data.get('context_filter')
        if context_filter_data:
            context_filter = ContextFilter.objects.create(docs_ids=context_filter_data['docs_ids'])
            chat_body.context_filter = context_filter
        
        chat_body.save()
        return chat_body

