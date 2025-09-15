#!/usr/bin/env python
"""
The code in chapter3/build_vectorsotres.py builds vector databases from PDF documents (GDPR, IRB, HIPAA) for use in document search and retrieval. It loads each PDF, splits it into text chunks, generates embeddings using either OpenAI or a local HuggingFace model, and stores the vectors using FAISS or Chroma. The script is configurable via command-line arguments and supports both cloud and local embedding backends.
"""
import os, argparse, re
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
# Choose either FAISS (simple, portable) or Chroma (server-like persistence)
USE_FAISS = True

load_dotenv()
gpt_key = os.getenv("GPT_KEY")
def chunk_pdf(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    # Add a simple page label to metadata for better traces
    for i, d in enumerate(chunks):
        d.metadata["source_file"] = os.path.basename(pdf_path)
    return chunks

def sanitize(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+","_", name).lower()

def build_store(pdf_path: str, out_dir: str, embeddings):
    chunks = chunk_pdf(pdf_path)
    os.makedirs(out_dir, exist_ok=True)

    if USE_FAISS:
        from langchain_community.vectorstores import FAISS
        vs = FAISS.from_documents(chunks, embeddings)
        vs.save_local(out_dir)
    else:
        from langchain_community.vectorstores import Chroma
        vs = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=out_dir)
        vs.persist()
    print(f"[OK] Built store: {out_dir} (chunks={len(chunks)})")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdpr", required=True)
    ap.add_argument("--irb", required=True)
    ap.add_argument("--hipaa", required=True)
    ap.add_argument("--out", default="./vectordb")
    ap.add_argument("--backend", choices=["openai","local"], default="openai")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Embeddings
    if args.backend == "openai":
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()  # uses text-embedding-3-large by default
    else:
        # Example local emb (swap to what you’ve installed; may need model download)
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    mapping = {
        "gdpr": args.gdpr,
        "irb": args.irb,
        "hipaa": args.hipaa
    }

    for name, path in mapping.items():
        out_dir = os.path.join(args.out, sanitize(name))
        build_store(path, out_dir, embeddings)

if __name__ == "__main__":
    main()
