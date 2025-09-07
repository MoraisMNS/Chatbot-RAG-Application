from src.config import OPENAI_API_KEY, PINECONE_INDEX, NAMESPACE
from src.helper import load_pdf_files, process_documents
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

embedding = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small",
    dimensions=1024,             
    disallowed_special=()
)

docs = load_pdf_files("Docs/")
splits = process_documents(docs)

vectorstore = PineconeVectorStore.from_documents(
    documents=splits,
    embedding=embedding,
    index_name=PINECONE_INDEX,
    namespace=NAMESPACE
)

print(f"Upserted {len(splits)} chunks into {PINECONE_INDEX}/{NAMESPACE}")
