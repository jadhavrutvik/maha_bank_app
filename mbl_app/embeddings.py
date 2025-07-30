import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

APP_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_STORE = os.path.join(APP_DIR, 'embeddings')
FAISS_INDEX_FILE = os.path.join(VECTOR_STORE, 'faiss.index')
TEXTS_FILE = os.path.join(VECTOR_STORE, 'texts.pkl')

def load_or_download_model():
    model_name = "all-MiniLM-L6-v2"
    local_path = os.path.join(APP_DIR, 'models')
    model_dir = os.path.join(local_path, model_name.replace("/", "_"))

    if os.path.exists(model_dir):
        return SentenceTransformer(model_dir)
    else:
        model = SentenceTransformer(model_name)
        model.save(model_dir)
        return model

def load_texts():
    texts = []
    output_dir = os.path.join(APP_DIR, 'scrapped_txt')
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(output_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(output_dir, filename), "r", encoding="utf-8") as f:
                texts.append(f.read())
    return texts

def create_embeddings(texts):
    model = load_or_download_model()
    os.makedirs(VECTOR_STORE, exist_ok=True)

    embeddings = model.encode(texts, convert_to_numpy=True)

    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)  
    index.add(embeddings)


    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(TEXTS_FILE, "wb") as f:
        pickle.dump(texts, f)

    return "Embeddings and FAISS index saved successfully."


def search_similar_chunks(question, top_k=3):
    model = load_or_download_model()

    index = faiss.read_index(FAISS_INDEX_FILE)
    with open(TEXTS_FILE, "rb") as f:
        texts = pickle.load(f)


    query_vector = model.encode([question], convert_to_numpy=True)
    distances, indices = index.search(query_vector, top_k)


    similar_chunks = [texts[i] for i in indices[0]]
    return similar_chunks
