"""Cognee RAG memory system for the AI agent."""

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import get_settings
from src.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MemoryChunk:
    """A chunk of memory with embedding."""
    id: Optional[str]
    text: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None


class CogneeMemory:
    """Cognee RAG-based memory system using sentence-transformers."""

    def __init__(
        self,
        embedding_model: Optional[str] = None,
        vector_store_path: Optional[str] = None,
    ):
        self.settings = get_settings()
        self.embedding_model_name = embedding_model or self.settings.cognee_embedding_model
        self.vector_store_path = vector_store_path or self.settings.cognee_vector_store
        self._model: Optional[SentenceTransformer] = None
        self._dimension: Optional[int] = None

    def _get_model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            logger.info(
                "Loading embedding model",
                model=self.embedding_model_name,
            )
            self._model = SentenceTransformer(self.embedding_model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(
                "Embedding model loaded",
                model=self.embedding_model_name,
                dimension=self._dimension,
            )
        return self._model

    @contextmanager
    def _get_db_connection(self):
        """Get SQLite database connection for vector store."""
        Path(self.vector_store_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.vector_store_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        """Ensure vector store schema exists."""
        with self._get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_chunks_created 
                ON memory_chunks(created_at)
            """)
            conn.commit()

    def _encode_text(self, text: str) -> List[float]:
        """Encode text to embedding vector."""
        model = self._get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def _embedding_to_bytes(self, embedding: List[float]) -> bytes:
        """Convert embedding list to bytes."""
        return np.array(embedding, dtype=np.float32).tobytes()

    def _bytes_to_embedding(self, data: bytes) -> List[float]:
        """Convert bytes to embedding list."""
        arr = np.frombuffer(data, dtype=np.float32)
        return arr.tolist()

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        dot = np.dot(a_arr, b_arr)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    async def add(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryChunk:
        """Add a memory chunk to the store."""
        self._ensure_schema()

        embedding = self._encode_text(text)
        embedding_bytes = self._embedding_to_bytes(embedding)
        metadata_json = json.dumps(metadata) if metadata else None

        with self._get_db_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO memory_chunks (text, embedding, metadata)
                VALUES (?, ?, ?)
                """,
                (text, embedding_bytes, metadata_json),
            )
            conn.commit()
            chunk_id = cursor.lastrowid

        logger.info(
            "Memory chunk added",
            chunk_id=chunk_id,
            text_length=len(text),
        )

        return MemoryChunk(
            id=str(chunk_id),
            text=text,
            embedding=embedding,
            metadata=metadata,
        )

    async def add_batch(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[MemoryChunk]:
        """Add multiple memory chunks in batch."""
        self._ensure_schema()

        if metadatas is None:
            metadatas = [None] * len(texts)

        # Encode all texts in batch (more efficient)
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)

        chunks = []
        with self._get_db_connection() as conn:
            for text, embedding_arr, metadata in zip(texts, embeddings, metadatas):
                embedding = embedding_arr.tolist()
                embedding_bytes = self._embedding_to_bytes(embedding)
                metadata_json = json.dumps(metadata) if metadata else None

                cursor = conn.execute(
                    """
                    INSERT INTO memory_chunks (text, embedding, metadata)
                    VALUES (?, ?, ?)
                    """,
                    (text, embedding_bytes, metadata_json),
                )
                chunk_id = cursor.lastrowid

                chunks.append(MemoryChunk(
                    id=str(chunk_id),
                    text=text,
                    embedding=embedding,
                    metadata=metadata,
                ))

            conn.commit()

        logger.info(
            "Memory chunks added in batch",
            count=len(chunks),
        )

        return chunks

    async def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
    ) -> List[MemoryChunk]:
        """Search for similar memory chunks."""
        self._ensure_schema()

        threshold = threshold or self.settings.cognee_similarity_threshold
        query_embedding = self._encode_text(query)

        with self._get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT id, text, embedding, metadata FROM memory_chunks"
            )
            rows = cursor.fetchall()

        results = []
        for row in rows:
            embedding = self._bytes_to_embedding(row["embedding"])
            similarity = self._cosine_similarity(query_embedding, embedding)

            if similarity >= threshold:
                metadata = json.loads(row["metadata"]) if row["metadata"] else None
                results.append(MemoryChunk(
                    id=str(row["id"]),
                    text=row["text"],
                    embedding=embedding,
                    metadata=metadata,
                    score=similarity,
                ))

        # Sort by similarity score
        results.sort(key=lambda x: x.score or 0, reverse=True)

        logger.info(
            "Memory search completed",
            query_length=len(query),
            results_found=len(results),
            top_k=top_k,
        )

        return results[:top_k]

    async def get_context(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> str:
        """Get relevant context for a query, formatted for LLM consumption."""
        if not self.settings.cognee_auto_context_window:
            chunks = await self.search(query, top_k=self.settings.cognee_max_results)
        else:
            # Adaptive context window based on query complexity
            chunks = await self.search(query, top_k=self.settings.cognee_max_results)

        if not chunks:
            return ""

        context_parts = []
        current_tokens = 0
        approx_tokens_per_char = 0.25

        for chunk in chunks:
            chunk_text = chunk.text
            chunk_tokens = int(len(chunk_text) * approx_tokens_per_char)

            if current_tokens + chunk_tokens > max_tokens:
                break

            context_parts.append(chunk_text)
            current_tokens += chunk_tokens

        return "\n\n---\n\n".join(context_parts)

    async def delete(self, chunk_id: str) -> bool:
        """Delete a memory chunk by ID."""
        with self._get_db_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM memory_chunks WHERE id = ?",
                (chunk_id,),
            )
            conn.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            logger.info("Memory chunk deleted", chunk_id=chunk_id)
        return deleted

    async def clear(self) -> int:
        """Clear all memory chunks. Returns count of deleted records."""
        with self._get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM memory_chunks")
            conn.commit()
            count = cursor.rowcount

        logger.info("All memory chunks cleared", count=count)
        return count

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        with self._get_db_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM memory_chunks")
            row = cursor.fetchone()
            total_chunks = row["count"] if row else 0

        return {
            "total_chunks": total_chunks,
            "embedding_model": self.embedding_model_name,
            "embedding_dimension": self._dimension,
            "vector_store_path": self.vector_store_path,
        }


# Singleton instance
_memory_instance: Optional[CogneeMemory] = None


def get_memory() -> CogneeMemory:
    """Get singleton memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = CogneeMemory()
    return _memory_instance


async def init_memory() -> CogneeMemory:
    """Initialize memory system."""
    memory = get_memory()
    memory._ensure_schema()
    return memory
