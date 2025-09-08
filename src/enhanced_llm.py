# src/enhanced_llm.py
from src.config import OPENAI_API_KEY
from src.pinecone_vectorstore import get_vectorstore
from src.prompt import contextualize_prompt, answer_prompt
from src.generative_ai import GenerativeAIEnhancer
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.prompts import ChatPromptTemplate
from typing import Dict, List, Any, Optional
import time

class EnhancedRAGChain:
    """Enhanced RAG Chain with Generative AI features"""
    
    def __init__(self):
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0)
        self.vectorstore = get_vectorstore()
        
        base_retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 8, "fetch_k": 24, "lambda_mult": 0.6}
        )
        
        compressor = LLMChainExtractor.from_llm(self.llm)
        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, self.compression_retriever, contextualize_prompt
        )
        
        self.qa_chain = create_stuff_documents_chain(self.llm, answer_prompt)
        
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)
        
        self.ai_enhancer = GenerativeAIEnhancer()
        
        self.enhanced_answer_prompt = ChatPromptTemplate.from_template("""
You are a highly advanced customer support assistant with sophisticated AI capabilities.

CONTEXT FROM COMPANY DOCUMENTS:
{context}

CONVERSATION HISTORY:
{chat_history}

CURRENT USER QUESTION: {input}

Generate a comprehensive, helpful response that:

1. **DIRECTLY ANSWERS** the user's question using the provided context
2. **INCORPORATES RELEVANT DETAILS** from company documentation
3. **MAINTAINS CONVERSATIONAL FLOW** with previous interactions
4. **PROVIDES ACTIONABLE GUIDANCE** when possible
5. **ACKNOWLEDGES LIMITATIONS** if information is incomplete
6. **USES PROFESSIONAL YET FRIENDLY TONE**

Key Guidelines:
- Start with a direct answer
- Support with specific details from documents
- Provide step-by-step instructions when relevant
- Suggest follow-up actions if appropriate
- Be concise but comprehensive
- Use bullet points for complex procedures

Response:
""")
    
    def enhanced_invoke(
        self, 
        query: str, 
        session_id: str,
        chat_history: List[Dict] = None,
        use_summarization: bool = True,
        generate_followups: bool = False
    ) -> Dict[str, Any]:
        """
        Enhanced invoke method with generative AI features
        """
        start_time = time.time()
        chat_history = chat_history or []
        
        try:
            enhanced_query = self.ai_enhancer.enhance_query_with_context(query, chat_history)
            
            retrieval_result = self.rag_chain.invoke({
                "input": enhanced_query,
                "chat_history": self._format_chat_history(chat_history)
            })
            
            retrieved_docs = retrieval_result.get("context", [])
            base_answer = retrieval_result.get("answer", "")
            
            enhanced_features = {}
            
            if use_summarization and retrieved_docs:
                enhanced_features["document_summary"] = self.ai_enhancer.summarize_documents(
                    retrieved_docs, query
                )
            
            enhanced_response = self.ai_enhancer.generate_contextual_response(
                query=query,
                retrieved_context=base_answer,
                chat_history=chat_history,
                user_intent=self._detect_intent(query)
            )
            
            if generate_followups:
                enhanced_features["follow_up_suggestions"] = self.ai_enhancer.generate_follow_up_suggestions(
                    query, enhanced_response, base_answer
                )

            processing_time = time.time() - start_time
            
            return {
                "answer": enhanced_response,
                "original_answer": base_answer,
                "context": retrieved_docs,
                "enhanced_features": enhanced_features,
                "metadata": {
                    "processing_time": processing_time,
                    "enhanced_query": enhanced_query,
                    "documents_retrieved": len(retrieved_docs),
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            fallback_result = self.rag_chain.invoke({
                "input": query,
                "chat_history": self._format_chat_history(chat_history)
            })
            
            return {
                "answer": fallback_result.get("answer", f"I encountered an error: {str(e)}"),
                "context": fallback_result.get("context", []),
                "enhanced_features": {"error": str(e)},
                "metadata": {"fallback_used": True, "session_id": session_id}
            }
    
    def generate_faqs(self, num_faqs: int = 10) -> List[Dict[str, str]]:
        """Generate FAQs from all documents in the vector store"""
        try:
            sample_queries = [
                "company policies", "customer service", "products", 
                "procedures", "guidelines", "support"
            ]
            
            all_docs = []
            for query in sample_queries:
                docs = self.vectorstore.similarity_search(query, k=3)
                all_docs.extend(docs)
            
            unique_docs = []
            seen_content = set()
            for doc in all_docs:
                if doc.page_content[:100] not in seen_content:
                    unique_docs.append(doc)
                    seen_content.add(doc.page_content[:100])
            
            return self.ai_enhancer.generate_faq_from_documents(unique_docs, num_faqs)
            
        except Exception as e:
            return [{"question": "Error generating FAQs", "answer": str(e)}]
    
    def analyze_document_content(self, limit: int = 20) -> Dict[str, Any]:
        """Analyze the content of indexed documents"""
        try:
            sample_docs = self.vectorstore.similarity_search("", k=limit)
            
            if not sample_docs:
                return {"error": "No documents found in vector store"}
            
            overall_summary = self.ai_enhancer.summarize_documents(
                sample_docs, 
                "Provide an overview of all company documentation"
            )
            
            faqs = self.ai_enhancer.generate_faq_from_documents(sample_docs, 5)
            
            return {
                "total_documents_analyzed": len(sample_docs),
                "overall_summary": overall_summary,
                "generated_faqs": faqs,
                "document_sources": list(set([
                    doc.metadata.get("source", "unknown") 
                    for doc in sample_docs
                ]))
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _format_chat_history(self, chat_history: List[Dict]) -> List:
        """Format chat history for LangChain"""
        formatted = []
        for msg in chat_history:
            if msg.get("type") == "user":
                formatted.append(("human", msg.get("content", "")))
            elif msg.get("type") == "bot":
                formatted.append(("ai", msg.get("content", "")))
        return formatted
    
    def _detect_intent(self, query: str) -> str:
        """Simple intent detection"""
        query_lower = query.lower()
        
        complaint_words = ["complaint", "problem", "issue", "wrong", "error", "bug", "broken"]
        request_words = ["please", "can you", "could you", "help me", "how to", "need"]
        inquiry_words = ["what", "how", "when", "where", "why", "tell me"]
        
        if any(word in query_lower for word in complaint_words):
            return "complaint"
        elif any(word in query_lower for word in request_words):
            return "request"
        elif any(word in query_lower for word in inquiry_words):
            return "inquiry"
        else:
            return "general"

enhanced_rag_chain = EnhancedRAGChain()

def get_enhanced_rag_chain():
    """Get the enhanced RAG chain instance"""
    return enhanced_rag_chain

def test_enhanced_features():
    """Test the enhanced features"""
    chain = get_enhanced_rag_chain()
    
    result = chain.enhanced_invoke(
        "How do I return a product?",
        "test_session",
        use_summarization=True,
        generate_followups=True
    )
    
    print("Enhanced Response:", result["answer"])
    print("Follow-ups:", result["enhanced_features"].get("follow_up_suggestions", []))
    
    faqs = chain.generate_faqs(5)
    print("Generated FAQs:", faqs)

if __name__ == "__main__":
    test_enhanced_features()