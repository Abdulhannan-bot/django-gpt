# from django.db import models
# from llama_index.types import TokenGen
# # from chunks_service import Chunk

# # Create your models here.
# class TokenGenField(models.TextField):
#     def from_db_value(self, value, expression, connection):
#         if value is None:
#             return None
#         return TokenGen(value)

#     def to_python(self, value):
#         if isinstance(value, TokenGen):
#             return value
#         if value is None:
#             return None
#         return TokenGen(value)

#     def get_prep_value(self, value):
#         if value is None:
#             return None
#         return str(value.data)
    
# class Chunk(models.Model):
#     object = models.CharField(max_length=255)  # Adjust the max_length as needed
#     score = models.FloatField(default=0.0)  # Field for score
#     document = models.ForeignKey(IngestedDoc, on_delete=models.CASCADE)  # ForeignKey relationship
#     text = models.TextField()  # Field for text
#     previous_texts = models.JSONField(null=True, blank=True)  # Field for previous_texts
#     next_texts = models.JSONField(null=True, blank=True)  # Field for next_texts

# class Completion(models.Model):
#     response = models.CharField(max_length=255, null = True, blank = True)
#     sources = models.ManyToManyField(Chunk, null=True, on_delete=models.CASCADE)

# class CompletionGen(models.Model):
#     response = TokenGenField()
#     sources = models.ManyToManyField(Chunk, null=True, on_delete=models.CASCADE)

