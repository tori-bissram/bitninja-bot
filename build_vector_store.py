import numpy as np
from PyPDF2 import PdfReader
import os
import json
import faiss
from embedding import get_embedding
from confluence_fetcher import get_confluence_content
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "docs"
INDEX_FILE = "bitninja_index.faiss"
METADATA_FILE = "bitninja_metadata.json"

def get_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def main():
    documents = []
    metadata = []

    # Process PDF files
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".pdf"):
                path = os.path.join(DATA_DIR, filename)
                text = get_pdf_text(path)
                documents.append(text)
                metadata.append({"source": f"PDF: {filename}", "text": text})

    # Fetch Confluence content
    print("Fetching Confluence content...")
    confluence_pages = get_confluence_content()
    for title, content in confluence_pages:
        documents.append(content)
        metadata.append({"source": f"Confluence: {title}", "text": content})

    if not documents:
        print("No documents found!")
        return

    print(f"Processing {len(documents)} documents...")
    
    # Generate embeddings using OpenAI
    embeddings = []
    for i, doc in enumerate(documents):
        print(f"Embedding document {i+1}/{len(documents)}")
        embedding = get_embedding(doc[:8000])  # Limit text length
        embeddings.append(embedding)

    embeddings = np.array(embeddings).astype('float32')
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index and metadata
    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)

    print(f"Vector store created with {len(documents)} documents!")

if __name__ == "__main__":
    main()
