import os
import json
import logging
import numpy as np
from pathlib import Path
from turbovec import IdMapIndex

logger = logging.getLogger("bejo.memory")

MEMORY_STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "memory_store")
EMBEDDING_DIM = 3072


def get_embedding(text: str) -> np.ndarray:
    try:
        from google import genai
        from google.genai import types
        client = genai.Client()
        result = client.models.embed_content(
            model="gemini-embedding-2",
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        return np.array(result.embeddings[0].values, dtype=np.float32)
    except Exception as e:
        logger.warning(f"Gemini embedding failed ({e}), using fallback hash embedding")
        rng = np.random.RandomState(hash(text) % (2 ** 31))
        vec = rng.randn(EMBEDDING_DIM).astype(np.float32)
        vec /= np.linalg.norm(vec)
        return vec


class SemanticMemory:
    def __init__(self, storage_dir: str = None, dim: int = EMBEDDING_DIM, bit_width: int = 4):
        self.dim = dim
        self.bit_width = bit_width
        self.storage_dir = Path(storage_dir or MEMORY_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.index: IdMapIndex = IdMapIndex(self.dim, self.bit_width)
        self.next_id: int = 0
        self.documents: dict[int, dict] = {}

        self._load()
        logger.info(f"SemanticMemory initialized: {len(self.index)} vectors, {len(self.documents)} docs")

    def add(self, text: str, metadata: dict = None) -> int:
        vec = get_embedding(text)
        if np.isnan(vec).any() or np.isinf(vec).any():
            logger.error(f"Invalid embedding for text: {text[:50]}...")
            return -1
        vec = np.ascontiguousarray(vec.reshape(1, -1))
        self.next_id += 1
        uid = np.array([self.next_id], dtype=np.uint64)
        self.index.add_with_ids(vec, uid)
        self.documents[self.next_id] = {"text": text, "metadata": metadata or {}}
        self._save()
        logger.info(f"Added doc #{self.next_id}: {text[:60]}...")
        return self.next_id

    def search(self, query: str, k: int = 5) -> list[dict]:
        if len(self.index) == 0:
            return []
        qvec = get_embedding(query)
        if np.isnan(qvec).any() or np.isinf(qvec).any():
            return []
        qvec = np.ascontiguousarray(qvec.reshape(1, -1))
        scores, ids = self.index.search(qvec, k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            doc = self.documents.get(int(idx))
            if doc:
                results.append({**doc, "score": float(score), "id": int(idx)})
        return results

    def search_by_metadata(self, query: str, metadata_filter: dict, k: int = 5) -> list[dict]:
        all_results = self.search(query, k=len(self.documents) or 1)
        filtered = []
        for r in all_results:
            if all(r.get("metadata", {}).get(k) == v for k, v in metadata_filter.items()):
                filtered.append(r)
        return filtered[:k]

    def remove(self, doc_id: int) -> bool:
        if doc_id in self.documents:
            self.index.remove(doc_id)
            del self.documents[doc_id]
            self._save()
            logger.info(f"Removed doc #{doc_id}")
            return True
        return False

    def clear(self):
        self.index = IdMapIndex(self.dim, self.bit_width)
        self.next_id = 0
        self.documents.clear()
        self._save()
        logger.info("SemanticMemory cleared")

    @property
    def count(self) -> int:
        return len(self.index)

    def _save(self):
        self.index.write(str(self.storage_dir / "index.tvim"))
        payload = {"next_id": self.next_id, "docs": {str(k): v for k, v in self.documents.items()}}
        with open(self.storage_dir / "docs.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def _load(self):
        idx_file = self.storage_dir / "index.tvim"
        doc_file = self.storage_dir / "docs.json"
        if idx_file.exists() and doc_file.exists():
            try:
                loaded = IdMapIndex.load(str(idx_file))
                test_vec = np.zeros((1, EMBEDDING_DIM), dtype=np.float32)
                test_vec = np.ascontiguousarray(test_vec)
                try:
                    loaded.search(test_vec, 1)
                except ValueError:
                    logger.warning(f"Index dim mismatch, rebuilding memory (expected {EMBEDDING_DIM})")
                    self.index = IdMapIndex(EMBEDDING_DIM, self.bit_width)
                    self.storage_dir.mkdir(parents=True, exist_ok=True)
                    self._save()
                    return
                self.index = loaded
                with open(doc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.next_id = data["next_id"]
                self.documents = {int(k): v for k, v in data["docs"].items()}
                logger.info(f"Loaded {len(self.index)} vectors from {self.storage_dir}")
            except Exception as e:
                logger.error(f"Failed to load memory store: {e}")
