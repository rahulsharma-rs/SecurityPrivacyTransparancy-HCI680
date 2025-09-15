#!/usr/bin/env python
"""
The code in chapter3/agent_with_tools.py implements a command-line Q&A agent that uses LangChain and OpenAI to answer questions about GDPR, IRB, and HIPAA regulations. It loads vector databases for each regulation, wraps them as search tools, and uses a language model to generate answers by searching these databases. The user can interactively ask questions, and the agent retrieves relevant legal text to support its responses.
"""

import os, argparse
from typing import List
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
load_dotenv()
gpt_key = os.getenv("GPT_KEY")
def load_vs(path: str):
    emb = OpenAIEmbeddings()
    return FAISS.load_local(path, emb, allow_dangerous_deserialization=True)

def build_tool(name: str, path: str, description: str) -> Tool:
    vs = load_vs(path)
    retriever = vs.as_retriever(search_kwargs={"k":4})
    def _search(q: str):
        docs = retriever.get_relevant_documents(q)
        joined = "\n\n".join([f"Source: {d.metadata.get('source_file')}\n{d.page_content}" for d in docs])
        return joined
    return Tool(name=name, func=_search, description=description)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./vectordb")
    args = ap.parse_args()

    tools: List[Tool] = [
        build_tool("GDPR_DB",  os.path.join(args.root, "gdpr"),  "Search GDPR text for legal basis, Art. 6, Art. 9, transfers."),
        build_tool("IRB_DB",   os.path.join(args.root, "irb"),   "Search IRB protocol/regulatory text (45 CFR 46)."),
        build_tool("HIPAA_DB", os.path.join(args.root, "hipaa"), "Search HIPAA Privacy/Security/Breach rules.")
    ]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    print("\nType your question (Ctrl+C to exit).")
    while True:
        q = input("\nQ> ")
        ans = agent.run(q)
        print(f"\nA> {ans}")

if __name__ == "__main__":
    main()
