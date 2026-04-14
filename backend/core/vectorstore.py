import faiss
import numpy as np
import json
import os
from typing import Optional

class VectorStore:
    def __init__(self, tenant_id: str, dim: int = 384, data_dir: str = None):
        self.tenant_id = tenant_id
        self.dim = dim
        self.data_dir = data_dir or os.getenv("DATA_DIR", "./data")
        self.tenant_dir = os.path.join(self.data_dir, tenant_id)
        self.index_path = os.path.join(self.tenant_dir, "index.faiss")
        self.meta_path = os.path.join(self.tenant_dir, "chunks.json")
        os.makedirs(self.tenant_dir, exist_ok=True)
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, 'r') as f:
                self.chunks = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.chunks = []
    
    def add(self, embeddings: np.ndarray, chunk_texts: list[str], sources: list[str]):
        if len(embeddings) == 0:
            return
        self.index.add(embeddings.astype('float32'))
        for text, source in zip(chunk_texts, sources):
            self.chunks.append({"text": text, "source": source})
        self.save()
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> tuple[list[int], list[float], list[dict]]:
        if self.index.ntotal == 0:
            return [], [], []
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding.reshape(1, -1).astype('float32'), k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                results.append({**self.chunks[idx], "score": float(distances[0][i])})
        return indices[0].tolist(), distances[0].tolist(), results
    
    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w') as f:
            json.dump(self.chunks, f)
    
    def count(self) -> int:
        return self.index.ntotal


_stores: dict[str, VectorStore] = {}

def get_vectorstore(tenant_id: str) -> VectorStore:
    if tenant_id not in _stores:
        _stores[tenant_id] = VectorStore(tenant_id)
    return _stores[tenant_id]
