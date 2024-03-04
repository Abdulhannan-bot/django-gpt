from django.db import models
import time
import uuid
from llama_index.llms import ChatResponse, CompletionResponse
# Create your models here.
from pydantic import BaseModel, Field
from typing import Literal
from chunks.models import Chunk

class ContextFilter(BaseModel):
    docs_ids: list[str] | None = Field(
        examples=[["c202d5e6-7b69-4869-81cc-dd574ee8ee11"]]
    )

# class ContextFilter(models.Model):
#     doc_id = models.CharField(max_length=255, null=True, blank=True)


# class OpenAIDelta(models.Model):
#     """A piece of completion that needs to be concatenated to get the full message."""

#     content = models.TextField(blank=True, null=True)
    
class OpenAIDelta(BaseModel):
    """A piece of completion that needs to be concatenated to get the full message."""

    content: str | None

# class OpenAIMessage(models.Model):
#     """Inference result, with the source of the message.

#     Role could be the assistant or system
#     (providing a default response, not AI generated).
#     """

#     ASSISTANT = 'assistant'
#     SYSTEM = 'system'
#     USER = 'user'
    
#     ROLE_CHOICES = [
#         (ASSISTANT, 'Assistant'),
#         (SYSTEM, 'System'),
#         (USER, 'User')
#     ]
    
#     role = models.CharField(max_length=100, choices=ROLE_CHOICES, default=USER)
#     content = models.TextField(blank=True, null=True)
    
class OpenAIMessage(BaseModel):
    """Inference result, with the source of the message.

    Role could be the assistant or system
    (providing a default response, not AI generated).
    """

    role: Literal["assistant", "system", "user"] = Field(default="user")
    content: str | None

# class OpenAIChoice(models.Model):
#     """Response from AI.

#     Either the delta or the message will be present, but never both.
#     Sources used will be returned in case context retrieval was enabled.
#     """

#     finish_reason = models.CharField(max_length=100, blank=True, null=True, choices=[("stop", "Stop")])
#     delta = models.OneToOneField(OpenAIDelta, on_delete=models.CASCADE, blank=True, null=True)
#     message = models.OneToOneField(OpenAIMessage, on_delete=models.CASCADE, blank=True, null=True)
#     index = models.IntegerField(default=0)
    
# class OpenAICompletion(models.Model):
#     """Clone of OpenAI Completion model.

#     For more information see: https://platform.openai.com/docs/api-reference/chat/object
#     """

#     COMPLETION = "completion"
#     COMPLETION_CHUNK = "completion.chunk"
    
#     OBJECT_CHOICES = [
#         (COMPLETION, "Completion"),
#         (COMPLETION_CHUNK, "Completion Chunk")
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     object = models.CharField(max_length=100, choices=OBJECT_CHOICES, default=COMPLETION)
#     created = models.IntegerField(default=int(time.time()))
#     model = models.CharField(max_length=100, default="private-gpt")
#     choices = models.ManyToManyField(OpenAIChoice)

#     @classmethod
#     def from_text(cls, text = None, finish_reason = None, sources = None):
#         completion = cls.objects.create(
#             model="private-gpt"
#         )
        
#         message = OpenAIMessage.objects.create(role=OpenAIMessage.ASSISTANT, content=text)
#         choice = OpenAIChoice.objects.create(message=message, finish_reason=finish_reason)
#         completion.choices.add(choice)
        
#         if sources:
#             completion.choices.sources.set(sources)

#         return completion

#     @classmethod
#     def from_delta(cls, text = None, finish_reason = None, sources = None):
#         completion = cls.objects.create(
#             model="private-gpt"
#         )
        
#         delta = OpenAIDelta.objects.create(content=text)
#         choice = OpenAIChoice.objects.create(delta=delta, finish_reason=finish_reason)
#         completion.choices.add(choice)
        
#         if sources:
#             completion.choices.sources.set(sources)

#         return completion

class OpenAIChoice(BaseModel):
    """Response from AI.

    Either the delta or the message will be present, but never both.
    Sources used will be returned in case context retrieval was enabled.
    """

    finish_reason: str | None = Field(examples=["stop"])
    delta: OpenAIDelta | None = None
    message: OpenAIMessage | None = None
    sources: list[Chunk] | None = None
    index: int = 0


class OpenAICompletion(BaseModel):
    """Clone of OpenAI Completion model.

    For more information see: https://platform.openai.com/docs/api-reference/chat/object
    """

    id: str
    object: Literal["completion", "completion.chunk"] = Field(default="completion")
    created: int = Field(..., examples=[1623340000])
    model: Literal["private-gpt"]
    choices: list[OpenAIChoice]

    @classmethod
    def from_text(
        cls,
        text: str | None,
        finish_reason: str | None = None,
        sources: list[Chunk] | None = None,
    ) -> "OpenAICompletion":
        return OpenAICompletion(
            id=str(uuid.uuid4()),
            object="completion",
            created=int(time.time()),
            model="private-gpt",
            choices=[
                OpenAIChoice(
                    message=OpenAIMessage(role="assistant", content=text),
                    finish_reason=finish_reason,
                    sources=sources,
                )
            ],
        )

    @classmethod
    def json_from_delta(
        cls,
        *,
        text: str | None,
        finish_reason: str | None = None,
        sources: list[Chunk] | None = None,
    ) -> str:
        chunk = OpenAICompletion(
            id=str(uuid.uuid4()),
            object="completion.chunk",
            created=int(time.time()),
            model="private-gpt",
            choices=[
                OpenAIChoice(
                    delta=OpenAIDelta(content=text),
                    finish_reason=finish_reason,
                    sources=sources,
                )
            ],
        )

        return chunk.model_dump_json()


def to_openai_response(response, sources = None):
    if isinstance(response, ChatResponse):
        return OpenAICompletion.from_text(response.delta, finish_reason="stop")
    else:
        return OpenAICompletion.from_text(response, finish_reason="stop", sources=sources)


def to_openai_sse_stream(response_generator, sources = None):
    for response in response_generator:
        if isinstance(response, (CompletionResponse, ChatResponse)):
            yield f"data: {OpenAICompletion.from_text(response.delta)}\n\n"
        else:
            yield f"data: {OpenAICompletion.from_text(response, sources=sources)}\n\n"
    yield f"data: {OpenAICompletion.from_text(finish_reason='stop')}\n\n"
    yield "data: [DONE]\n\n"
