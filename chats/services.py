from dataclasses import dataclass

from injector import inject, singleton
from llama_index import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.chat_engine import ContextChatEngine, SimpleChatEngine
from llama_index.chat_engine.types import (
    BaseChatEngine,
)
from llama_index.indices.postprocessor import MetadataReplacementPostProcessor
from llama_index.llms import ChatMessage, MessageRole


from .models import Completion, CompletionGen

from components.embeddings.embedding_component import EmbeddingComponent
from components.llm.llm_component import LLMComponent
from components.node_store.node_store_component import NodeStoreComponent
from components.vector_store.vector_store_component import (
    VectorStoreComponent,
)
from open_ai.models import ContextFilter
from chunks.models import Chunk



@dataclass
class ChatEngineInput:
    system_message = None
    last_message = None
    chat_history = None

    @classmethod
    def from_messages(cls, messages):
        # Detect if there is a system message, extract the last message and chat history
        system_message = (
            messages[0]
            if len(messages) > 0 and messages[0].role == MessageRole.SYSTEM
            else None
        )
        last_message = (
            messages[-1]
            if len(messages) > 0 and messages[-1].role == MessageRole.USER
            else None
        )
        # Remove from messages list the system message and last message,
        # if they exist. The rest is the chat history.
        if system_message:
            messages.pop(0)
        if last_message:
            messages.pop(-1)
        chat_history = messages if len(messages) > 0 else None

        return cls(
            system_message=system_message,
            last_message=last_message,
            chat_history=chat_history,
        )


@singleton
class ChatService:
    @inject
    def __init__(
        self,
        llm_component,
        vector_store_component,
        embedding_component,
        node_store_component,
    ):
        self.llm_service = llm_component
        self.vector_store_component = vector_store_component
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store_component.vector_store,
            docstore=node_store_component.doc_store,
            index_store=node_store_component.index_store,
        )
        self.service_context = ServiceContext.from_defaults(
            llm=llm_component.llm, embed_model=embedding_component.embedding_model
        )
        self.index = VectorStoreIndex.from_vector_store(
            vector_store_component.vector_store,
            storage_context=self.storage_context,
            service_context=self.service_context,
            show_progress=True,
        )

    def _chat_engine(
        self,
        system_prompt = None,
        use_context = False,
        context_filter = None,
    ):
        if use_context:
            vector_index_retriever = self.vector_store_component.get_retriever(
                index=self.index, context_filter=context_filter
            )
            return ContextChatEngine.from_defaults(
                system_prompt=system_prompt,
                retriever=vector_index_retriever,
                service_context=self.service_context,
                node_postprocessors=[
                    MetadataReplacementPostProcessor(target_metadata_key="window"),
                ],
            )
        else:
            return SimpleChatEngine.from_defaults(
                system_prompt=system_prompt,
                service_context=self.service_context,
            )

    def stream_chat(
        self,
        messages,
        use_context= False,
        context_filter = None,
    ):
        chat_engine_input = ChatEngineInput.from_messages(messages)
        last_message = (
            chat_engine_input.last_message.content
            if chat_engine_input.last_message
            else None
        )
        system_prompt = (
            chat_engine_input.system_message.content
            if chat_engine_input.system_message
            else None
        )
        chat_history = (
            chat_engine_input.chat_history if chat_engine_input.chat_history else None
        )

        chat_engine = self._chat_engine(
            system_prompt=system_prompt,
            use_context=use_context,
            context_filter=context_filter,
        )
        streaming_response = chat_engine.stream_chat(
            message=last_message if last_message is not None else "",
            chat_history=chat_history,
        )
        sources = [Chunk.from_node(node) for node in streaming_response.source_nodes]
        completion_gen = CompletionGen(
            response=streaming_response.response_gen, sources=sources
        )
        return completion_gen

    def chat(
        self,
        messages,
        use_context = False,
        context_filter = None,
    ):
        chat_engine_input = ChatEngineInput.from_messages(messages)
        last_message = (
            chat_engine_input.last_message.content
            if chat_engine_input.last_message
            else None
        )
        system_prompt = (
            chat_engine_input.system_message.content
            if chat_engine_input.system_message
            else None
        )
        chat_history = (
            chat_engine_input.chat_history if chat_engine_input.chat_history else None
        )

        chat_engine = self._chat_engine(
            system_prompt=system_prompt,
            use_context=use_context,
            context_filter=context_filter,
        )
        wrapped_response = chat_engine.chat(
            message=last_message if last_message is not None else "",
            chat_history=chat_history,
        )
        sources = [Chunk.from_node(node) for node in wrapped_response.source_nodes]
        completion = Completion(response=wrapped_response.response, sources=sources)
        return completion
