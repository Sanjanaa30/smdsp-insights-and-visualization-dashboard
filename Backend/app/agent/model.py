from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://llm.gauravshivaprasad.com/v1")
    BASE_URL = "https://api.3ya.io/api/v1"
    CLIENT_ID: str = os.getenv("CLIENT_ID", "")
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET", "")


settings = Settings()

llm = ChatOpenAI(
    model="o3",
    base_url=settings.BASE_URL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0,
)
