from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key="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",
    temperature=0,
)
