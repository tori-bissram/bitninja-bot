import os
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# CONFIG
DOCS_DIR = "docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
INDEX_FILE = "bitninja_index.faiss"
METADATA_FILE = "bitninja_metadata.json"

# Load model
model = SentenceTransformer(EMBEDDING_MODEL)

# Prepare data
texts = []
filenames = []

for fname in os.listdir(DOCS_DIR):
    fpath = os.path.join(DOCS_DIR, fname)
    if os.path.isfile(fpath) and fname.endswith(".txt"):
        with open(fpath, "r", encoding="utf-8") as f:
            texts.append(f.read())
            filenames.append(fname)

# Embed texts
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

# Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index + metadata
faiss.write_index(index, INDEX_FILE)

with open(METADATA_FILE, "w") as f:
    json.dump(list(zip(filenames, texts)), f)

print(f"Indexed {len(filenames)} documents.")
