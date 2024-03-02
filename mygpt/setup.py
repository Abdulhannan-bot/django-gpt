#!/usr/bin/env python3
import os
import argparse

from huggingface_hub import hf_hub_download, snapshot_download, login

login(token="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")

from transformers import AutoTokenizer

from settings import (
    MODELS_PATH,
    MODELS_CACHE_PATH,
    LLM_HF_MODEL_NAME,
    LLM_HF_MODEL_FILE,
    EMBEDDINGS_HF_MODEL_NAME,
    LLM_TOKENIZER
)


resume_download = True
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Setup: Download models from huggingface')
    parser.add_argument('--resume', default=True, action=argparse.BooleanOptionalAction, help='Enable/Disable resume_download options to restart the download progress interrupted')
    args = parser.parse_args()
    resume_download = args.resume

os.makedirs(MODELS_PATH, exist_ok=True)

# Download Embedding model
embedding_path = MODELS_PATH / "embedding"
print(f"Downloading embedding {LLM_HF_MODEL_NAME}")
snapshot_download(
    repo_id=EMBEDDINGS_HF_MODEL_NAME,
    cache_dir=MODELS_CACHE_PATH,
    local_dir=embedding_path,
)
print("Embedding model downloaded!")

# Download LLM and create a symlink to the model file
print(f"Downloading LLM {LLM_HF_MODEL_FILE}")
hf_hub_download(
    repo_id=LLM_HF_MODEL_NAME,
    filename=LLM_HF_MODEL_FILE,
    cache_dir=MODELS_CACHE_PATH,
    local_dir=MODELS_PATH,
    resume_download=resume_download,
)
print("LLM model downloaded!")

# Download Tokenizer
print(f"Downloading tokenizer {LLM_TOKENIZER}")
AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path=LLM_TOKENIZER,
    cache_dir=MODELS_CACHE_PATH,
)

print("Tokenizer downloaded!")

print("Setup done")