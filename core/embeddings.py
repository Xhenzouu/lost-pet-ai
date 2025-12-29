# core/embeddings.py

import torch
import numpy as np
from PIL import Image
from pathlib import Path
from torchvision import models, transforms

# -------------------------------
# Load pretrained CNN (ResNet50)
# -------------------------------
_resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
_resnet.eval()

# Remove classification head → embeddings
_model = torch.nn.Sequential(*list(_resnet.children())[:-1])

# -------------------------------
# Image preprocessing
# -------------------------------
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# -------------------------------
# Generate embedding
# -------------------------------
def generate_image_embedding(image_path: str) -> list:
    """
    Convert an image into a 2048-dim embedding vector.
    Stored later as JSONB.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")
    tensor = _transform(image).unsqueeze(0)

    with torch.no_grad():
        embedding = _model(tensor)

    # Shape: (1, 2048, 1, 1) → (2048,)
    embedding = embedding.squeeze().numpy()

    return embedding.tolist()
