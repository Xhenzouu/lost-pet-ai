import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Optional

EMBEDDING_DIM = 512
EPS = 1e-8


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    return vec / (norm + EPS)


def generate_image_embedding(image_path: str) -> List[float]:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    img = Image.open(path).convert("RGB").resize((224, 224))
    arr = np.array(img)

    hist = np.histogramdd(
        arr.reshape(-1, 3),
        bins=(8, 8, 8),
        range=((0, 256), (0, 256), (0, 256))
    )[0]

    vec = hist.flatten().astype(np.float32)
    vec = _normalize(vec)

    return vec.tolist()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + EPS))


def compute_similarity_score(
    query_embedding: List[float],
    reference_embeddings: List[List[float]],
    top_k: int = 5
) -> Optional[float]:
    """
    Unsupervised similarity score in [0, 1].
    Uses top-K cosine similarity against known embeddings.
    """

    if not reference_embeddings:
        return None

    q = _normalize(np.array(query_embedding, dtype=np.float32))
    refs = [_normalize(np.array(e, dtype=np.float32)) for e in reference_embeddings if e]

    if not refs:
        return None

    sims = [cosine_similarity(q, r) for r in refs]
    sims.sort(reverse=True)

    top_sims = sims[:top_k]
    return float(np.mean(top_sims))