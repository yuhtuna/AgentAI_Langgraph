import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure the LLM to use Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
