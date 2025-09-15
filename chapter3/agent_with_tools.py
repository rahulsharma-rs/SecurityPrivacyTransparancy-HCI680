#!/usr/bin/env python
"""
Q&A Agent for Privacy Regulations (HIPAA, GDPR, IRB)

This script implements a command-line agent that can answer questions
about HIPAA, GDPR, and IRB regulations. It uses:
- Vector databases (FAISS) that store regulation text.
- LangChain tools to search those databases.
- An OpenAI language model to generate supported answers.

Lecture Link: Week 3 (Slide 11) – "Building a Regulation-Aware Q&A Agent"
"""

import textwrap
import os, argparse
from typing import List
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load API key (from .env file in the project root)
load_dotenv()
gpt_key = os.getenv("GPT_KEY")

# ---------- Helper Functions ----------

def load_vs(path: str):
    """
    Load a FAISS vector store from disk.
    Each store is built from legal text (HIPAA, GDPR, IRB).
    OpenAI embeddings are used for similarity search.
    """
    emb = OpenAIEmbeddings()
    return FAISS.load_local(path, emb, allow_dangerous_deserialization=True)

def build_tool(name: str, path: str, description: str) -> Tool:
    """
    Wrap a vector store as a LangChain Tool.
    Each tool lets the agent query one regulation.
    """
    vs = load_vs(path)
    retriever = vs.as_retriever(search_kwargs={"k":4})  # top-4 relevant chunks

    def _search(q: str):
        # Fetch relevant text passages
        docs = retriever.get_relevant_documents(q)
        # Return combined results with source info
        joined = "\n\n".join(
            [f"Source: {d.metadata.get('source_file')}\n{d.page_content}" for d in docs]
        )
        return joined

    return Tool(name=name, func=_search, description=description)

# ---------- Main Agent ----------

def main():
    # Parse command-line argument for vector DB root folder
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./vectordb")
    args = ap.parse_args()

    # Build search tools for GDPR, IRB, and HIPAA
    tools: List[Tool] = [
        build_tool("GDPR_DB",  os.path.join(args.root, "gdpr"),
                   "Search GDPR text for legal basis, Art. 6, Art. 9, transfers."),
        build_tool("IRB_DB",   os.path.join(args.root, "irb"),
                   "Search IRB protocol/regulatory text (45 CFR 46)."),
        build_tool("HIPAA_DB", os.path.join(args.root, "hipaa"),
                   "Search HIPAA Privacy/Security/Breach rules.")
    ]

    # Initialize a GPT-4o-mini agent with tool access
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = initialize_agent(
        tools, llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # Interactive Q&A loop
    print("\nType your question (Ctrl+C to exit).")
    while True:
        q = input("\nQ> ")
        ans = agent.run(q)

        # Print formatted answer
        print("=" * 60)
        print("Answer:\n")
        print(textwrap.fill(ans, width=80))
        print("=" * 60)

# ---------- Script Entry Point ----------
if __name__ == "__main__":
    main()
