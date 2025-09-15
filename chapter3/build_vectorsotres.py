#!/usr/bin/env python
"""
Build Vector Stores from Regulation PDFs (HIPAA, GDPR, IRB)

This script processes PDF documents (HIPAA, GDPR, IRB), splits them into chunks,
creates embeddings, and saves them in a vector database (FAISS or Chroma).
These vector stores are later used by the Q&A agent (agent_with_tools.py).

---------------------------------------------------------
Usage Example:

# Using OpenAI embeddings (requires GPT_KEY in .env file):
python build_vectorsotres.py \
  --gdpr ./GDPR.pdf \
  --hipaa ./HIPAA.pdf \
  --irb ./IRB.pdf \
  --out ./vectordb \
  --backend openai

# Using local HuggingFace embeddings (no API key needed):
python build_vectorsotres.py \
  --gdpr ./GDPR.pdf \
  --hipaa ./HIPAA.pdf \
  --irb ./IRB.pdf \
  --out ./vectordb \
  --backend local
---------------------------------------------------------
"""

import os, argparse, re
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Default: FAISS backend (simple + portable).
# Change to False to use Chroma for persistence.
USE_FAISS = True

# Load API key from .env if using OpenAI embeddings
load_dotenv()
gpt_key = os.getenv("GPT_KEY")

def chunk_pdf(pdf_path: str):
    """
    Load and split a PDF into overlapping text chunks.
    Each chunk keeps reference metadata (filename).
    """
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,   # max characters per chunk
        chunk_overlap=150  # overlap for context continuity
    )
    chunks = splitter.split_documents(docs)

    # Add filename metadata for traceability
    for i, d in enumerate(chunks):
        d.metadata["source_file"] = os.path.basename(pdf_path)
    return chunks

def sanitize(name: str) -> str:
    """
    Clean string for use in directory naming.
    Removes invalid characters, lowercase only.
    """
    return re.sub(r"[^a-zA-Z0-9_-]+","_", name).lower()

def build_store(pdf_path: str, out_dir: str, embeddings):
    """
    Build and save a vector store from one PDF.
    Saves FAISS (default) or Chroma database locally.
    """
    chunks = chunk_pdf(pdf_path)
    os.makedirs(out_dir, exist_ok=True)

    if USE_FAISS:
        from langchain_community.vectorstores import FAISS
        vs = FAISS.from_documents(chunks, embeddings)
        vs.save_local(out_dir)
    else:
        from langchain_community.vectorstores import Chroma
        vs = Chroma.from_documents(chunks, embedding=embeddings,
                                   persist_directory=out_dir)
        vs.persist()
    print(f"[OK] Built store: {out_dir} (chunks={len(chunks)})")

def main():
    # Parse command-line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdpr", required=True, help="Path to GDPR PDF")
    ap.add_argument("--irb", required=True, help="Path to IRB PDF")
    ap.add_argument("--hipaa", required=True, help="Path to HIPAA PDF")
    ap.add_argument("--out", default="./vectordb", help="Output folder")
    ap.add_argument("--backend", choices=["openai","local"], default="openai",
                    help="Choose embedding backend")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Choose embeddings backend
    if args.backend == "openai":
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()  # default: text-embedding-3-large
    else:
        # Local HuggingFace embeddings (requires sentence-transformers installed)
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    # Map each regulation to its PDF
    mapping = {
        "gdpr": args.gdpr,
        "irb": args.irb,
        "hipaa": args.hipaa
    }

    # Build vector store for each PDF
    for name, path in mapping.items():
        out_dir = os.path.join(args.out, sanitize(name))
        build_store(path, out_dir, embeddings)

if __name__ == "__main__":
    main()
