"""
This script uses a GPT-based language model to analyze an anonymized healthcare dataset for re-identification risks. It loads the dataset from a CSV file, formats it into a prompt, and asks the AI agent to assess k-anonymity, l-diversity, and quasi-identifiers, then prints the analysis.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import os
from numpy.distutils.system_info import dfftw_info
from dotenv import load_dotenv
load_dotenv()
gpt_key = os.getenv("GPT_KEY")
template = """
You are a compliance AI agent. Analyze this limited dataset for re-identification risks.
Consider k-anonymity, l-diversity, and quasi-identifiers.
Dataset:
{data}
"""

prompt = PromptTemplate(template=template, input_variables=["data"])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = LLMChain(llm=llm, prompt=prompt)
df_anon = pd.read_csv("anonymized_health_data.csv")
analysis = chain.run({"data": df_anon.to_string(index=False)})
print("AI Agent Analysis:\n", analysis)