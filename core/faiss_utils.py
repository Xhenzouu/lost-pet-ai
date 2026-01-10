import faiss
import numpy as np
import json
from pathlib import Path
from core.models.lost_pet_model import LostPetModel

FAISS_DIR = Path(__file__).parent.parent / "faiss_index"
FAISS_DIR.mkdir(exist_ok=True)
INDEX_FILE = FAISS_DIR / "pet_embeddings.index"
ID_MAP_FILE = FAISS_DIR / "pet_ids.json"


def build_faiss_index() -> faiss.IndexFlatL2:
    """
    Build a FAISS index from all existing pet embeddings.
    Returns the FAISS index and saves pet IDs for retrieval.
    """
    embeddings = LostPetModel.get_existing_embeddings()
    if not embeddings:
        raise ValueError("No embeddings found to build FAISS index.")

    embeddings_array = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(embeddings_array.shape[1])
    index.add(embeddings_array)

    faiss.write_index(index, str(INDEX_FILE))

    pet_ids = list(range(len(embeddings)))
    with open(ID_MAP_FILE, "w") as f:
        json.dump(pet_ids, f)

    return index


def load_faiss_index() -> faiss.IndexFlatL2:
    """
    Load FAISS index from disk.
    """
    if not INDEX_FILE.exists():
        raise FileNotFoundError("FAISS index not found. Build it first.")
    return faiss.read_index(str(INDEX_FILE))


def query_faiss_index(query_embedding: list, top_k: int = 5):
    """
    Query the FAISS index to find most similar embeddings.
    Returns list of (pet_id, distance).
    """
    index = load_faiss_index()

    query_vec = np.array(query_embedding, dtype="float32").reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)

    with open(ID_MAP_FILE, "r") as f:
        pet_ids = json.load(f)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        pet_id = pet_ids[idx] if idx < len(pet_ids) else None
        if pet_id is not None:
            results.append((pet_id, float(dist)))

    return results