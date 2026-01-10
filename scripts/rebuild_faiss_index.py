# scripts/rebuild_faiss_index.py

import sys
from pathlib import Path
import logging
import numpy as np
import faiss

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.models.lost_pet_model import LostPetModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def rebuild_faiss_index():
    embeddings = LostPetModel.get_existing_embeddings()
    num_embeddings = len(embeddings)

    if num_embeddings == 0:
        logger.warning("No embeddings found with correct dimension. FAISS index not created.")
        return

    embeddings_array = np.array(embeddings, dtype=np.float32)

    index = faiss.IndexFlatL2(LostPetModel.EMBEDDING_DIM)
    index.add(embeddings_array)
    logger.info(f"Added {num_embeddings} embeddings to FAISS index.")

    faiss_index_path = LostPetModel.FAISS_INDEX_PATH
    faiss_index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(faiss_index_path))
    logger.info(f"FAISS index saved at: {faiss_index_path}")

if __name__ == "__main__":
    rebuild_faiss_index()