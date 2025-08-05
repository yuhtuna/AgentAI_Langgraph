import os
from dotenv import load_dotenv
from openai import OpenAI
# Load .env file
load_dotenv()


load_dotenv()

# Create OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Use with LangChain
from langchain_community.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="google/gemini-pro-1.5",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY")
)
