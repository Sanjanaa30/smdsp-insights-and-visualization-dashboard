from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
llm_api_key = os.getenv("OPENAI_API_KEY")
llm_model = os.getenv("LLM_MODEL", "gpt-4.1-mini")

llm = ChatOpenAI(
    model=llm_model,
    api_key=llm_api_key,
    temperature=0,
)
