from sentence_transformers import SentenceTransformer
import numpy as np
import os
from typing import Optional

class Embedder:
    def __init__(self, model_name: str = None, dim: int = None):
        model_name = model_name or os.getenv("EMBEDDER_MODEL", "all-MiniLM-L6-v2")
        self.dim = dim or int(os.getenv("EMBEDDING_DIM", "384"))
        self.model = SentenceTransformer(model_name)
    
    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.array([]).reshape(0, self.dim)
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.astype('float32')
    
    def embed_single(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


_embedder: Optional[Embedder] = None

def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder
