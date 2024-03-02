from django.db import models
from llama_index.schema import NodeWithScore
from ingests.models import IngestedDoc
# Create your models here.

class Chunk(models.Model):
    object = models.CharField(max_length=255)  # Adjust the max_length as needed
    score = models.FloatField(default=0.0)  # Field for score
    document = models.ForeignKey(IngestedDoc, on_delete=models.CASCADE)  # ForeignKey relationship
    text = models.TextField()  # Field for text
    previous_texts = models.JSONField(null=True, blank=True)  # Field for previous_texts
    next_texts = models.JSONField(null=True, blank=True)  # Field for next_texts

    @classmethod
    def from_node(cls: type["Chunk"], node: NodeWithScore) -> "Chunk":
        doc_id = node.node.ref_doc_id if node.node.ref_doc_id is not None else "-"
        return cls(
            object="context.chunk",
            score=node.score or 0.0,
            document=IngestedDoc(
                object="ingest.document",
                doc_id=doc_id,
                doc_metadata=node.metadata,
            ),
            text=node.get_content(),
        )
    
class ChatBody(models.Model):
    model_config = models.JSONField()

    use_context = models.BooleanField(default=False)
    include_sources = models.BooleanField(default=True)
    stream = models.BooleanField(default=False)
    
    def messages(self):
        return OpenAIMessage.objects.filter(chat_body=self)
    
    @classmethod
    def from_json(cls, json_data):
        return cls.objects.create(model_config=json_data['model_config'], use_context=json_data.get('use_context', False), include_sources=json_data.get('include_sources', True), stream=json_data.get('stream', False))