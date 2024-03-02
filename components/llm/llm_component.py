import logging

from injector import inject, singleton
from llama_index import set_global_tokenizer
from llama_index.llms import MockLLM
from llama_index.llms.base import LLM
from transformers import AutoTokenizer  # type: ignore

from components.llm.prompt_helper import get_prompt_style
# from private_gpt.paths import models_cache_path, models_path
from mygpt.settings import (
    MODELS_CACHE_PATH,
    MODELS_PATH,
    LLM_TOKENIZER,
    LLM_MODE,
    PROMPT_STYLE,
    LLM_HF_MODEL_FILE,
    MAX_NEW_TOKENS,
    CONTEXT_WINDOW
)
# from private_gpt.settings.settings import Settings

logger = logging.getLogger(__name__)


@singleton
class LLMComponent:
    llm = None

    @inject
    def __init__(self):
        llm_mode = LLM_MODE
        if LLM_TOKENIZER:
            set_global_tokenizer(
                AutoTokenizer.from_pretrained(
                    pretrained_model_name_or_path=LLM_TOKENIZER,
                    cache_dir=str(MODELS_CACHE_PATH),
                )
            )

        logger.info("Initializing the LLM in mode=%s", llm_mode)
        
        match llm_mode:
            case "local":
                from llama_index.llms import LlamaCPP
                print(MODELS_PATH)
                prompt_style = get_prompt_style(PROMPT_STYLE)

                self.llm = LlamaCPP(
                    model_path=str(MODELS_PATH / LLM_HF_MODEL_FILE),
                    temperature=0.1,
                    max_new_tokens=MAX_NEW_TOKENS,
                    context_window=CONTEXT_WINDOW,
                    generate_kwargs={},
                    # All to GPU
                    model_kwargs={"n_gpu_layers": -1, "offload_kqv": True},
                    # transform inputs into Llama2 format
                    messages_to_prompt=prompt_style.messages_to_prompt,
                    completion_to_prompt=prompt_style.completion_to_prompt,
                    verbose=True,
                    n_ctx = int(512),
                    n_batch = int(512),
                )

            case "sagemaker":
                from private_gpt.components.llm.custom.sagemaker import SagemakerLLM

                self.llm = SagemakerLLM(
                    endpoint_name=settings.sagemaker.llm_endpoint_name,
                    max_new_tokens=settings.llm.max_new_tokens,
                    context_window=settings.llm.context_window,
                )
            case "openai":
                from llama_index.llms import OpenAI

                openai_settings = settings.openai
                self.llm = OpenAI(
                    api_base=openai_settings.api_base,
                    api_key=openai_settings.api_key,
                    model=openai_settings.model,
                )
            case "openailike":
                from llama_index.llms import OpenAILike

                openai_settings = settings.openai
                self.llm = OpenAILike(
                    api_base=openai_settings.api_base,
                    api_key=openai_settings.api_key,
                    model=openai_settings.model,
                    is_chat_model=True,
                    max_tokens=None,
                    api_version="",
                )
            case "mock":
                self.llm = MockLLM()
            case "ollama":
                from llama_index.llms import Ollama

                ollama_settings = settings.ollama
                self.llm = Ollama(
                    model=ollama_settings.model, base_url=ollama_settings.api_base
                )
