import os
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from src.pinecone_vectorstore import vectorstore
from src.prompt import *
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set.")

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4o",
    temperature=0
)


retriever = vectorstore.as_retriever(
    search_k=15,
    search_by_vector=True,
    search_type="similarity",
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_prompt
)


qa_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)