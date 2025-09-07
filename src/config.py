# src/config.py
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") or ""
PINECONE_INDEX = os.getenv("PINECONE_INDEX") or "ai-chatbot"
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "test")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set")
