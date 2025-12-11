import os
from dotenv import load_dotenv
from openai import OpenAI
# Load .env file
load_dotenv()


load_dotenv()

# Create OpenAI client
base_url = os.getenv("OPENROUTER_API_BASE_URL", "https://openrouter.ai/api/v1")
api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

# Use with LangChain
from langchain_community.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="google/gemini-pro-1.5",
    openai_api_base=base_url,
    openai_api_key=api_key
)