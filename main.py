import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain / OpenAI / Pinecone
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore  # Use this instead
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Retrieval upgrades
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

if OPENAI_API_KEY is None or LANGCHAIN_API_KEY is None:
    print("error")
else:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    # Langsmith tracking
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

class QueryModel(BaseModel):
    session_id: str
    input: str

app = FastAPI()  # Enable docs for testing

allowed_origins = ["*"]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3
)

# Fixed: Added dimensions=1024 to match your Pinecone index
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=1024
)

# Use existing Pinecone index instead of recreating
vectorstore = PineconeVectorStore(
    index_name=PINECONE_INDEX,
    embedding=embedding_model,
    namespace="test"  # Same namespace used in store_index.py
)

retriever = vectorstore.as_retriever(
    search_k=15,
    search_type="similarity",
)

contextualize_system_prompt = (
    "Using chat history and the latest user question, reformulate the question if needed, otherwise return it as is."
)

contextualize_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        ("assistant", 
     "First, list the 1-3 most relevant context snippets (with section titles) "
     "and why they are relevant. Then answer concisely for a business user. "
     "If context is insufficient, ask one precise follow-up.")
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_prompt
)

system_prompt = (
    "You are an intelligent chatbot designed to provide information exclusively about company-related topics, such as HR policies, security policies, and other company-related information. Also You have been given the user manual of Gallery HR. Assist with queries regarding the user manual with the given information. Our company is Soft Gallery (PVT) LTD, a software development company. further informations are also provided. When you have been asked a question, it means someone needs information related to our company or about the Gallery HR. You must act as a friendly and gentle assistant in charge of giving relevant answers to what information they need. Ask them about their specific question or issue regarding the company policies or GalleryHR-related things. Be sure to gather all necessary details to address their inquiry. If you are not clear about what they are asking for, ask only one question at a time and understand their queries. Your job is to provide support, not to collect information. Use only the provided context to answer questions. Follow these guidelines strictly: 1. Only answer questions directly related to the given context. 2. Do not respond to unrelated topics such as general knowledge, science, mathematics, etc. 3. Avoid performing general tasks like writing essays or providing code. 4. Never disclose the names of documents or their authors. 5. Don't mention that you have been provided documents, just that according to the information you have. 6. Don't mention or give any info about the version of the document. Additionally, do not give mixed-up answers and general ideas."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
qa_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

@app.get("/")
async def read_root():
    try:
        return "Hello World !!!"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
def get_session_history_by_sessionid(session_id: str):
    try:
        return get_session_history(session_id)
    except Exception:
        if session_id not in store:
            raise HTTPException(status_code=404, detail="Session ID not found")
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/history/{session_id}")
def delete_session_history_by_sessionid(session_id: str):
    try:
        if session_id in store:
            del store[session_id]
        return "Deleted"
    except Exception:
        if session_id not in store:
            raise HTTPException(status_code=404, detail="Session ID not found")
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/query")
async def query(request: Request, query: QueryModel):
    try:
        response = conversational_rag_chain.invoke(
            {"input": query.input},
            config={"configurable": {"session_id": query.session_id}},
        )
        return {"answer": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))