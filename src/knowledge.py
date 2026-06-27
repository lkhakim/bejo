import os
import json
import logging
import numpy as np
from pathlib import Path
from turbovec import IdMapIndex

logger = logging.getLogger("bejo.knowledge")

STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "knowledge_store")
EMBEDDING_DIM = 3072


def _make_embedding(text: str) -> np.ndarray:
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
        logger.warning(f"Embedding fallback ({e})")
        rng = np.random.RandomState(hash(text) % (2 ** 31))
        vec = rng.randn(EMBEDDING_DIM).astype(np.float32)
        vec /= np.linalg.norm(vec)
        return vec


class KnowledgeBase:
    def __init__(self, storage_dir: str = None):
        self.storage_dir = Path(storage_dir or STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index = IdMapIndex(EMBEDDING_DIM, 4)
        self.next_id = 0
        self.entries = {}

        self._load()
        logger.info(f"KnowledgeBase loaded: {len(self.entries)} entries")

    def add(self, question: str, answer: str, tags: list = None) -> int:
        text = question.strip()
        if not text:
            return -1
        vec = _make_embedding(text)
        if np.isnan(vec).any() or np.isinf(vec).any():
            return -1
        vec = np.ascontiguousarray(vec.reshape(1, -1))
        self.next_id += 1
        uid = np.array([self.next_id], dtype=np.uint64)
        self.index.add_with_ids(vec, uid)
        self.entries[self.next_id] = {
            "question": question,
            "answer": answer,
            "tags": tags or [],
        }
        self._save()
        logger.info(f"KB added #{self.next_id}: {question[:60]}")
        return self.next_id

    def search(self, query: str, k: int = 3, threshold: float = 0.6) -> list[dict]:
        if len(self.index) == 0:
            return []
        qvec = _make_embedding(query)
        if np.isnan(qvec).any() or np.isinf(qvec).any():
            return []
        qvec = np.ascontiguousarray(qvec.reshape(1, -1))
        scores, ids = self.index.search(qvec, k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            entry = self.entries.get(int(idx))
            if entry and float(score) >= threshold:
                results.append({
                    "id": int(idx),
                    "question": entry["question"],
                    "answer": entry["answer"],
                    "score": float(score),
                })
        return results

    def answer(self, query: str, threshold: float = 0.6) -> str | None:
        results = self.search(query, k=1, threshold=threshold)
        if results:
            return results[0]["answer"]
        return None

    def list_all(self) -> list[dict]:
        return [
            {"id": eid, **entry}
            for eid, entry in sorted(self.entries.items())
        ]

    def remove(self, entry_id: int) -> bool:
        if entry_id in self.entries:
            self.index.remove(entry_id)
            del self.entries[entry_id]
            self._save()
            logger.info(f"KB removed #{entry_id}")
            return True
        return False

    def count(self) -> int:
        return len(self.entries)

    def _save(self):
        self.index.write(str(self.storage_dir / "index.tvim"))
        payload = {"next_id": self.next_id, "entries": {str(k): v for k, v in self.entries.items()}}
        with open(self.storage_dir / "kb.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def _load(self):
        idx_file = self.storage_dir / "index.tvim"
        kb_file = self.storage_dir / "kb.json"
        if idx_file.exists() and kb_file.exists():
            try:
                loaded = IdMapIndex.load(str(idx_file))
                test_vec = np.zeros((1, EMBEDDING_DIM), dtype=np.float32)
                test_vec = np.ascontiguousarray(test_vec)
                try:
                    loaded.search(test_vec, 1)
                except ValueError:
                    logger.warning(f"Index dim mismatch, rebuilding store (expected {EMBEDDING_DIM})")
                    self.index = IdMapIndex(EMBEDDING_DIM, 4)
                    self.storage_dir.mkdir(parents=True, exist_ok=True)
                    self._save()
                    return
                self.index = loaded
                with open(kb_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.next_id = data["next_id"]
                self.entries = {int(k): v for k, v in data["entries"].items()}
            except Exception as e:
                logger.error(f"Failed to load knowledge base: {e}")
