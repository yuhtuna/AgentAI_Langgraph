import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure the LLM for production use with OpenRouter API
from langchain_community.chat_models import ChatOpenAI

# Initialize the LLM with OpenRouter configuration
llm = ChatOpenAI(
    model="google/gemini-pro-1.5",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY")
)
