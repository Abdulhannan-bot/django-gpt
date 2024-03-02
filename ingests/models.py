from django.db import models

# Create your models here.

class IngestedDoc(models.Model):
    object = models.CharField(max_length=255, default="ingest.document")  # Adjust the max_length as needed
    doc_id = models.CharField(max_length=255)  # Adjust the max_length as needed
    doc_metadata = models.JSONField(null=True, blank=True)  # Field for doc_metadata, as a JSONField

    @staticmethod
    def curate_metadata(metadata):
        """Remove unwanted metadata keys."""
        unwanted_keys = ["doc_id", "window", "original_text"]
        for key in unwanted_keys:
            metadata.pop(key, None)
        return metadata

    @classmethod
    def from_document(cls, document):
        return cls(
            doc_id=document.doc_id,
            doc_metadata=cls.curate_metadata(document.metadata),
        )
