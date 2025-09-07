import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set.")

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", None)
if PINECONE_API_KEY is None:
    raise ValueError("PINECONE_API_KEY is not set.")

PINECONE_INDEX = os.environ.get("PINECONE_INDEX", None)
if PINECONE_INDEX is None:
    raise ValueError("PINECONE_INDEX is not set.")

embedding_model = OpenAIEmbeddings( api_key=OPENAI_API_KEY, model="text-embedding-3-small", disallowed_special=())

def retrieve_from_existing_pinecone_vectorstore():
    return PineconeVectorStore.from_existing_index(embedding=embedding_model,index_name=PINECONE_INDEX, namespace="test" )


vectorstore = retrieve_from_existing_pinecone_vectorstore()