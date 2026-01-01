# core/embeddings.py

import numpy as np
from PIL import Image
from pathlib import Path
from typing import List

def generate_image_embedding(image_path: str) -> List[float]:
    """
    Generate a 512-dim RGB color histogram embedding.
    """
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

    vec = hist.flatten()
    vec = vec / (np.linalg.norm(vec) + 1e-8)
    return vec.tolist()