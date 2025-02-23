from typing import Any, List, Optional

import chardet

from dbgpt.rag.chunk import Document
from dbgpt.rag.knowledge.base import (
    ChunkStrategy,
    DocumentType,
    Knowledge,
    KnowledgeType,
)


class TXTKnowledge(Knowledge):
    """TXT Knowledge"""

    def __init__(
        self,
        file_path: Optional[str] = None,
        knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT,
        loader: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with Knowledge arguments.
        Args:
            file_path:(Optional[str]) file path
            knowledge_type:(KnowledgeType) knowledge type
            loader:(Optional[Any]) loader
        """
        self._path = file_path
        self._type = knowledge_type
        self._loader = loader

    def _load(self) -> List[Document]:
        """Load txt document from loader"""
        if self._loader:
            documents = self._loader.load()
        else:
            with open(self._path, "rb") as f:
                raw_text = f.read()
                result = chardet.detect(raw_text)
                if result["encoding"] is None:
                    text = raw_text.decode("utf-8")
                else:
                    text = raw_text.decode(result["encoding"])
            metadata = {"source": self._path}
            return [Document(content=text, metadata=metadata)]

        return [Document.langchain2doc(lc_document) for lc_document in documents]

    @classmethod
    def support_chunk_strategy(cls):
        return [
            ChunkStrategy.CHUNK_BY_SIZE,
            ChunkStrategy.CHUNK_BY_SEPARATOR,
        ]

    @classmethod
    def default_chunk_strategy(cls) -> ChunkStrategy:
        return ChunkStrategy.CHUNK_BY_SIZE

    @classmethod
    def type(cls) -> KnowledgeType:
        return KnowledgeType.DOCUMENT

    @classmethod
    def document_type(cls) -> DocumentType:
        return DocumentType.TXT
