import numpy as np
import os

# Force CPU mode before importing torch/transformers to avoid CUDA DLL errors on Windows
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Lazy-load model to avoid heavy import at module import time
_model = None

def _get_model():
    global _model
    if _model is None:
        # Import here to avoid import-time failure when sentence-transformers
        # or its heavy dependencies (torch/tensorflow) are not installed.
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device="cpu")
    return _model

def get_embedding(text: str) -> list:
    """Return embedding vector for given text as Python list (float32).

    Keeps the model in memory between calls. Imports SentenceTransformer lazily.
    """
    model = _get_model()
    emb = model.encode(text, show_progress_bar=False)
    # Ensure native python list of floats
    if isinstance(emb, np.ndarray):
        return emb.astype(float).tolist()
    return [float(x) for x in emb]
