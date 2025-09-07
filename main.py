from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.llm import rag_chain

class QueryModel(BaseModel):
    session_id: str
    input: str

app = FastAPI()

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
