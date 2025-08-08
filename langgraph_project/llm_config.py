import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# Load .env file
load_dotenv()


# Configure the LLM to use Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
