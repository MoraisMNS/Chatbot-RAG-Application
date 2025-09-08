# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime
import json

from src.llm import rag_chain  
from src.ingest import ingest_pdf_bytes, ingest_folder

from src.enhanced_llm import get_enhanced_rag_chain

class QueryModel(BaseModel):
    session_id: str
    input: str
    use_enhancements: bool = True
    generate_followups: bool = False

class EnhancedQueryModel(BaseModel):
    session_id: str
    input: str
    use_summarization: bool = True
    generate_followups: bool = True
    response_style: str = "professional"  

class FAQRequest(BaseModel):
    num_faqs: int = 10

app = FastAPI(title="Enhanced Customer Support AI", version="2.0")

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

enhanced_chain = get_enhanced_rag_chain()

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
def health():
    return {
        "status": "ok", 
        "service": "enhanced-customer-support-ai",
        "version": "2.0",
        "features": [
            "Advanced RAG",
            "Document Summarization",
            "Enhanced Response Generation",
            "FAQ Auto-Generation",
            "Follow-up Suggestions",
            "Intent Detection"
        ]
    }

@app.post("/query")
async def query(query: QueryModel):
    """Original query endpoint (maintained for backward compatibility)"""
    try:
        if query.use_enhancements:
            chat_history = get_chat_history_for_session(query.session_id)
            
            result = enhanced_chain.enhanced_invoke(
                query=query.input,
                session_id=query.session_id,
                chat_history=chat_history,
                use_summarization=True,
                generate_followups=query.generate_followups
            )
            
            update_chat_history(query.session_id, query.input, result["answer"])
            
            response = {
                "answer": result["answer"],
                "enhanced_features": result.get("enhanced_features", {}),
                "metadata": result.get("metadata", {})
            }
            
            return response
        else:
            response = conversational_rag_chain.invoke(
                {"input": query.input},
                config={"configurable": {"session_id": query.session_id}},
            )
            return {"answer": response["answer"]}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/enhanced")
async def enhanced_query(query: EnhancedQueryModel):
    """New enhanced query endpoint with full generative AI features"""
    try:
        start_time = time.time()

        chat_history = get_chat_history_for_session(query.session_id)

        result = enhanced_chain.enhanced_invoke(
            query=query.input,
            session_id=query.session_id,
            chat_history=chat_history,
            use_summarization=query.use_summarization,
            generate_followups=query.generate_followups
        )
        
        update_chat_history(query.session_id, query.input, result["answer"])
        
        response = {
            "answer": result["answer"],
            "enhanced_features": result.get("enhanced_features", {}),
            "metadata": {
                **result.get("metadata", {}),
                "total_processing_time": time.time() - start_time,
                "enhancement_used": True
            },
            "suggestions": result.get("enhanced_features", {}).get("follow_up_suggestions", []),
            "document_summary": result.get("enhanced_features", {}).get("document_summary"),
            "context_documents": len(result.get("context", []))
        }
        
        return response
        
    except Exception as e:
        try:
            fallback_response = conversational_rag_chain.invoke(
                {"input": query.input},
                config={"configurable": {"session_id": query.session_id}},
            )
            return {
                "answer": fallback_response["answer"],
                "metadata": {"fallback_used": True, "error": str(e)}
            }
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=str(fallback_error))

@app.post("/generate-faqs")
async def generate_faqs(request: FAQRequest):
    """Generate FAQs from indexed documents"""
    try:
        faqs = enhanced_chain.generate_faqs(request.num_faqs)
        return {
            "faqs": faqs,
            "total_generated": len(faqs),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/documents")
async def analyze_documents():
    """Analyze indexed documents and provide insights"""
    try:
        analysis = enhanced_chain.analyze_document_content()
        return {
            "analysis": analysis,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}/history")
async def get_session_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = get_chat_history_for_session(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}/history")
async def clear_session_history(session_id: str):
    """Clear chat history for a session"""
    try:
        if session_id in store:
            store[session_id].clear()

        session_key = f"chat_history_{session_id}"
        if session_key in store:
            del store[session_key]
        
        return {"status": "cleared", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/response-variations")
async def generate_response_variations(
    response_text: str = Query(..., description="Original response text"),
    num_variations: int = Query(3, description="Number of variations to generate")
):
    """Generate multiple variations of a response for A/B testing"""
    try:
        from src.generative_ai import GenerativeAIEnhancer
        enhancer = GenerativeAIEnhancer()
        
        variations = enhancer.generate_response_variations(response_text, num_variations)
        
        return {
            "original_response": response_text,
            "variations": variations,
            "total_variations": len(variations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize/documents")
async def summarize_documents(
    query: str = Query("", description="Optional query to focus summarization"),
    max_docs: int = Query(10, description="Maximum number of documents to summarize")
):
    """Summarize documents from the vector store"""
    try:
        from src.generative_ai import GenerativeAIEnhancer
        enhancer = GenerativeAIEnhancer()
        
        vectorstore = enhanced_chain.vectorstore
        
        if query:
            docs = vectorstore.similarity_search(query, k=max_docs)
        else:
            sample_queries = ["policies", "procedures", "guidelines", "support"]
            docs = []
            for q in sample_queries:
                docs.extend(vectorstore.similarity_search(q, k=max_docs//4))
        
        summary = enhancer.summarize_documents(docs, query)
        
        return {
            "summary": summary,
            "documents_summarized": len(docs),
            "focus_query": query or "general overview"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/usage")
async def get_usage_stats():
    """Get usage statistics"""
    try:
        total_sessions = len(store)
        
        total_messages = 0
        active_sessions = 0
        
        for session_id, history in store.items():
            if hasattr(history, 'messages'):
                session_msgs = len(history.messages)
                total_messages += session_msgs
                if session_msgs > 0:
                    active_sessions += 1
        
        chat_history_sessions = len([k for k in store.keys() if k.startswith("chat_history_")])
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "chat_history_sessions": chat_history_sessions,
            "average_messages_per_session": total_messages / max(active_sessions, 1),
            "timestamp": datetime.utcnow().isoformat()
        }
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


def get_chat_history_for_session(session_id: str) -> List[Dict[str, Any]]:
    """Get formatted chat history for a session"""
    session_key = f"chat_history_{session_id}"
    
    if session_key not in store:
        store[session_key] = []
    
    return store[session_key]

def update_chat_history(session_id: str, user_message: str, bot_response: str):
    """Update chat history with new messages"""
    session_key = f"chat_history_{session_id}"
    
    if session_key not in store:
        store[session_key] = []
    
    timestamp = datetime.utcnow().strftime("%H:%M:%S")
    
    store[session_key].append({
        "type": "user",
        "content": user_message,
        "timestamp": timestamp
    })
    
    store[session_key].append({
        "type": "bot", 
        "content": bot_response,
        "timestamp": timestamp
    })
    
    if len(store[session_key]) > 20:
        store[session_key] = store[session_key][-20:]


@app.post("/test/ai-approaches")
async def test_ai_approaches(
    query: str = Query(..., description="Test query"),
    session_id: str = Query("test_session", description="Session ID")
):
    """Test different AI approaches side by side"""
    try:
        results = {}
        
        try:
            original_result = conversational_rag_chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": f"{session_id}_original"}},
            )
            results["original_rag"] = {
                "answer": original_result["answer"],
                "approach": "Traditional RAG"
            }
        except Exception as e:
            results["original_rag"] = {"error": str(e)}
        
        try:
            enhanced_result = enhanced_chain.enhanced_invoke(
                query=query,
                session_id=f"{session_id}_enhanced",
                use_summarization=True,
                generate_followups=False
            )
            results["enhanced_with_summarization"] = {
                "answer": enhanced_result["answer"],
                "approach": "Enhanced RAG with Summarization",
                "summary": enhanced_result.get("enhanced_features", {}).get("document_summary")
            }
        except Exception as e:
            results["enhanced_with_summarization"] = {"error": str(e)}
        
        try:
            full_enhanced = enhanced_chain.enhanced_invoke(
                query=query,
                session_id=f"{session_id}_full",
                use_summarization=True,
                generate_followups=True
            )
            results["full_enhanced"] = {
                "answer": full_enhanced["answer"],
                "approach": "Full Enhanced RAG",
                "features": full_enhanced.get("enhanced_features", {}),
                "metadata": full_enhanced.get("metadata", {})
            }
        except Exception as e:
            results["full_enhanced"] = {"error": str(e)}
        
        return {
            "query": query,
            "approaches_tested": list(results.keys()),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)