from fastapi import FastAPI, HTTPException,UploadFile, File, BackgroundTasks, Query
from pydantic import BaseModel
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.llm import rag_chain
from src.ingest import ingest_pdf_bytes, ingest_folder
from fastapi.middleware.cors import CORSMiddleware

class QueryModel(BaseModel):
    session_id: str
    input: str

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Health check for Streamlit
@app.get("/")
def health():
    return {"status": "ok", "service": "gallery-hr-assistant"}

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

@app.post("/query")
async def query(query: QueryModel):
    try:
        response = conversational_rag_chain.invoke(
            {"input": query.input},
            config={"configurable": {"session_id": query.session_id}},
        )
        return {"answer": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ingest/file")
async def ingest_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    sync: bool = Query(False, description="If true, block until ingest finishes.")
):
    try:
        data = await file.read()
        if sync:
            result = ingest_pdf_bytes(data, file.filename)
            return {"status": "done", **result}
        else:
            background_tasks.add_task(ingest_pdf_bytes, data, file.filename)
            return {"status": "accepted", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: reindex the Docs/ folder on demand ---
@app.post("/ingest/folder")
def ingest_docs_folder(
    background_tasks: BackgroundTasks,
    path: str = Query("Docs/", description="Folder path"),
    sync: bool = Query(False)
):
    try:
        if sync:
            result = ingest_folder(path)
            return {"status": "done", **result}
        else:
            background_tasks.add_task(ingest_folder, path)
            return {"status": "accepted", "folder": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

