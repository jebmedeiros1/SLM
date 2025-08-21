import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import pandas as pd
import xml.etree.ElementTree as ET

model = SentenceTransformer('all-MiniLM-L6-v2')
index = None
documents = []

def read_document(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    content = ""
    if ext == ".pdf":
        reader = PdfReader(file_path)
        content = "\n".join([page.extract_text() or "" for page in reader.pages])
    elif ext == ".csv":
        df = pd.read_csv(file_path)
        content = df.to_string()
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
        content = df.to_string()
    elif ext == ".xml":
        tree = ET.parse(file_path)
        content = ET.tostring(tree.getroot(), encoding="unicode")
    return content

def add_documents_to_index(folder="docs"):
    global index, documents
    all_texts = []
    documents.clear()
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if not os.path.isfile(path): continue
        text = read_document(path)
        documents.append((file, text))
        all_texts.append(text)
    
    embeddings = model.encode(all_texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

def search_similar_documents(query, k=1):
    if not index:
        return "", []
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb), k)
    results = [(documents[i][1], documents[i][0]) for i in I[0]]
    context = "\n".join([r[0] for r in results])
    sources = [r[1] for r in results]
    return context, sources

