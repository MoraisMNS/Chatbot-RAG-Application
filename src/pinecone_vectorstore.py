from src.config import OPENAI_API_KEY, PINECONE_INDEX, NAMESPACE
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

_embedding = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small",
    dimensions=1024,             
    disallowed_special=()
)

def get_vectorstore():
    return PineconeVectorStore(
        index_name=PINECONE_INDEX,
        embedding=_embedding,
        namespace=NAMESPACE
    )
