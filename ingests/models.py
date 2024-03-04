from django.db import models
from typing import Any, Literal

from llama_index import Document
from pydantic import BaseModel, Field
# Create your models here.

# class IngestedDoc(models.Model):
#     object = models.CharField(max_length=255, default="ingest.document")  # Adjust the max_length as needed
#     doc_id = models.CharField(max_length=255)  # Adjust the max_length as needed
#     doc_metadata = models.JSONField(null=True, blank=True)  # Field for doc_metadata, as a JSONField

#     @staticmethod
#     def curate_metadata(metadata):
#         """Remove unwanted metadata keys."""
#         unwanted_keys = ["doc_id", "window", "original_text"]
#         for key in unwanted_keys:
#             metadata.pop(key, None)
#         return metadata

#     @classmethod
#     def from_document(cls, document):
#         return cls(
#             doc_id=document.doc_id,
#             doc_metadata=cls.curate_metadata(document.metadata),
#         )

class IngestedDoc(BaseModel):
    object: Literal["ingest.document"]
    doc_id: str = Field(examples=["c202d5e6-7b69-4869-81cc-dd574ee8ee11"])
    doc_metadata: dict[str, Any] | None = Field(
        examples=[
            {
                "page_label": "2",
                "file_name": "Sales Report Q3 2023.pdf",
            }
        ]
    )

    @staticmethod
    def curate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        """Remove unwanted metadata keys."""
        for key in ["doc_id", "window", "original_text"]:
            metadata.pop(key, None)
        return metadata

    @staticmethod
    def from_document(document: Document) -> "IngestedDoc":
        return IngestedDoc(
            object="ingest.document",
            doc_id=document.doc_id,
            doc_metadata=IngestedDoc.curate_metadata(document.metadata),
        )

