"""
ChromaDB Vector Store Service
Stores document embeddings for semantic search and AI reasoning.
Runs in-process — no separate Docker container needed.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-backed vector store for document embeddings."""

    def __init__(self):
        self._client = None
        self._collection = None
        self._embedder = None
        self._ready = False
        self._init()

    def _init(self):
        try:
            import chromadb
            from chromadb.config import Settings

            persist_dir = os.path.join(os.getcwd(), "chromadb_data")
            os.makedirs(persist_dir, exist_ok=True)

            self._client = chromadb.PersistentClient(path=persist_dir)
            self._collection = self._client.get_or_create_collection(
                name="intellicredit_documents",
                metadata={"hnsw:space": "cosine"},
            )
            self._ready = True
            logger.info("ChromaDB vector store initialised")
        except ImportError:
            logger.warning("chromadb not installed — vector store disabled")
        except Exception as e:
            logger.warning(f"ChromaDB init failed: {e} — continuing without vector store")

    def _embed(self, text: str) -> list[float]:
        """Generate embedding using sentence-transformers or simple TF-IDF fallback."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Loaded SentenceTransformer: all-MiniLM-L6-v2")
            except ImportError:
                logger.warning("sentence-transformers not installed — using hash embedding")
                self._embedder = "hash"

        if self._embedder == "hash":
            # Simple deterministic fallback (not useful for real similarity — demo only)
            import hashlib
            h = int(hashlib.md5(text.encode()).hexdigest(), 16)
            import random
            random.seed(h)
            return [random.gauss(0, 1) for _ in range(384)]

        return self._embedder.encode(text, normalize_embeddings=True).tolist()

    def add_document(self, doc_id: str, company_id: str, text: str, metadata: dict = None) -> bool:
        """Add a document chunk to the vector store."""
        if not self._ready or not text.strip():
            return False
        try:
            # Split into chunks to avoid ChromaDB size limits
            chunks = self._chunk_text(text, chunk_size=500)
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            embeddings = [self._embed(chunk) for chunk in chunks]
            metas = [{
                "doc_id": doc_id,
                "company_id": company_id,
                "chunk_index": i,
                **(metadata or {}),
            } for i in range(len(chunks))]

            self._collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metas,
            )
            logger.info(f"Added {len(chunks)} chunks for document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to vector store: {e}")
            return False

    def search(self, query: str, company_id: str = None, top_k: int = 5) -> list[dict]:
        """Search for similar document chunks."""
        if not self._ready:
            return []
        try:
            query_embedding = self._embed(query)
            where = {"company_id": company_id} if company_id else None
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count() or 1),
                where=where,
            )
            if not results["documents"]:
                return []
            return [
                {
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else None,
                }
                for i in range(len(results["documents"][0]))
            ]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def search_risk_signals(self, company_id: str) -> list[str]:
        """
        Search for risk-related text in company documents.
        Returns relevant text chunks for NLP analysis.
        """
        risk_queries = [
            "fraud investigation penalty fine",
            "default loan NPA insolvency",
            "regulatory action SEBI RBI",
            "lawsuit litigation court",
        ]
        seen = set()
        results = []
        for query in risk_queries:
            hits = self.search(query, company_id=company_id, top_k=2)
            for h in hits:
                text = h["text"]
                if text not in seen:
                    seen.add(text)
                    results.append(text)
        return results

    def _chunk_text(self, text: str, chunk_size: int = 500) -> list[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - 50):  # 50-word overlap
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks or [text[:2000]]  # fallback: first 2000 chars

    @property
    def is_ready(self) -> bool:
        return self._ready


# Singleton
vector_store = VectorStore()
