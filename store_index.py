import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from src.helper import load_pdf_files, process_documents
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")

embedding_model = OpenAIEmbeddings( api_key=OPENAI_API_KEY, 
                                   model="text-embedding-3-small", 
                                    dimensions=1024, 
                                   disallowed_special=())

pdf_folder_path = "Docs/"
extracted_documents = load_pdf_files(pdf_folder_path)
splits = process_documents(extracted_documents)

PineconeVectorStore.from_texts([t.page_content for t in splits], embedding=embedding_model,index_name=PINECONE_INDEX, namespace="test" )