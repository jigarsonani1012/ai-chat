import json
from pathlib import Path

import faiss
import numpy as np

from app.core.config import settings


class FaissVectorStore:
    def __init__(self, bot_id: str) -> None:
        self.bot_id = bot_id
        self.base_path = Path(settings.vector_store_path)
        self.index_path = self.base_path / f"{bot_id}.index"
        self.meta_path = self.base_path / f"{bot_id}.json"

    def upsert(self, vectors: list[list[float]], metadata: list[dict]) -> None:
        if not vectors:
            return

        matrix = np.array(vectors, dtype="float32")
        dimension = matrix.shape[1]

        if self.index_path.exists():
            index = faiss.read_index(str(self.index_path))
            stored_metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
        else:
            index = faiss.IndexFlatIP(dimension)
            stored_metadata = []

        faiss.normalize_L2(matrix)
        index.add(matrix)
        stored_metadata.extend(metadata)

        faiss.write_index(index, str(self.index_path))
        self.meta_path.write_text(json.dumps(stored_metadata), encoding="utf-8")

    def search(self, vector: list[float], limit: int = 5) -> list[dict]:
        if not vector or not self.index_path.exists():
            return []

        index = faiss.read_index(str(self.index_path))
        metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
        query = np.array([vector], dtype="float32")
        faiss.normalize_L2(query)
        scores, indices = index.search(query, limit)

        matches: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx >= len(metadata):
                continue
            item = metadata[idx]
            item["score"] = float(score)
            matches.append(item)
        return matches
