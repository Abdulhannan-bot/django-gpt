import logging
from typing import Literal
from injector import inject, singleton
from llama_index import MockEmbedding
from llama_index.embeddings.base import BaseEmbedding



from mygpt.settings import (
    MODELS_CACHE_PATH,
    EMBEDDINGS_HF_MODEL_NAME
)

logger = logging.getLogger(__name__)


@singleton
class EmbeddingComponent:
    embedding_model = None

    @inject
    def __init__(self):
        embedding_mode = Literal["local", "openai", "sagemaker", "mock"]
        logger.info("Initializing the embedding model in mode=%s", embedding_mode)
        match embedding_mode:
            case "local":
                from llama_index.embeddings import HuggingFaceEmbedding

                self.embedding_model = HuggingFaceEmbedding(
                    model_name=EMBEDDINGS_HF_MODEL_NAME,
                    cache_folder=str(MODELS_CACHE_PATH),
                )
            # case "openai":
            #     from llama_index import OpenAIEmbedding

            #     openai_settings = settings.openai.api_key
            #     self.embedding_model = OpenAIEmbedding(api_key=openai_settings)
            # case "mock":
            #     # Not a random number, is the dimensionality used by
            #     # the default embedding model
            #     self.embedding_model = MockEmbedding(384)
