import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

# Force CPU mode before importing torch/transformers to avoid CUDA DLL errors on Windows
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Lazy-load model to avoid heavy import at module import time
_model = None

def _get_model():
    global _model
    if _model is None:
        logger.info("Initializing SentenceTransformer model...")
        # Import here to avoid import-time failure when sentence-transformers
        # or its heavy dependencies (torch/tensorflow) are not installed.
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device="cpu")
        logger.info("Model initialized successfully")
    return _model

def get_embedding(text: str) -> list:
    """Return embedding vector for given text as Python list (float32).

    Keeps the model in memory between calls. Imports SentenceTransformer lazily.
    """
    logger.debug("Generating embedding for text of length: %d", len(text))
    model = _get_model()
    emb = model.encode(text, show_progress_bar=False)
    logger.debug("Raw embedding shape: %s, dtype: %s", emb.shape if hasattr(emb, 'shape') else 'N/A', type(emb))
    
    # Ensure native python list of floats
    if isinstance(emb, np.ndarray):
        result = emb.astype(float).tolist()
    else:
        result = [float(x) for x in emb]
    
    logger.info("Generated embedding with dimension: %d", len(result))
    logger.debug("Embedding sample (first 5 values): %s", result[:5])
    
    return result
