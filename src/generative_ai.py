# src/generative_ai_enhancements.py
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from src.config import OPENAI_API_KEY
import json
import re

class GenerativeAIEnhancer:
    """Advanced Generative AI features for the customer support chatbot"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4o",
            temperature=0.3
        )
        self.creative_llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4o",
            temperature=0.7
        )
    
    def summarize_documents(self, documents: List[Document], query: str = "") -> str:
        """
        Advanced document summarization with query-focused approach
        """
        if not documents:
            return "No relevant documents found."
        
        combined_content = "\n\n".join([doc.page_content for doc in documents[:5]])
        
        if len(combined_content) > 8000:
            combined_content = combined_content[:8000] + "..."
        
        summarization_prompt = ChatPromptTemplate.from_template("""
You are an expert document summarizer for a customer support system.

USER QUERY: {query}

DOCUMENTS TO SUMMARIZE:
{documents}

Create a comprehensive yet concise summary that:
1. Directly addresses the user's query if provided
2. Highlights the most important information from the documents
3. Maintains key details like procedures, policies, and specific instructions
4. Uses clear, customer-friendly language
5. Organizes information logically

SUMMARY:
""")
        
        chain = summarization_prompt | self.llm
        
        try:
            response = chain.invoke({
                "query": query or "general information",
                "documents": combined_content
            })
            return response.content
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def generate_contextual_response(
        self, 
        query: str, 
        retrieved_context: str, 
        chat_history: List[Dict] = None,
        user_intent: str = "inquiry"
    ) -> str:
        """
        Enhanced response generation with context awareness and intent consideration
        """
        chat_history = chat_history or []
        
        history_context = ""
        if chat_history:
            recent_history = chat_history[-3:]  
            history_context = "\n".join([
                f"User: {msg.get('content', '')}" if msg.get('type') == 'user' 
                else f"Assistant: {msg.get('content', '')}"
                for msg in recent_history
            ])
        
        response_prompt = ChatPromptTemplate.from_template("""
You are an expert customer support assistant with advanced AI capabilities.

CONVERSATION CONTEXT:
{history_context}

CURRENT USER QUERY: {query}
DETECTED INTENT: {intent}

RETRIEVED COMPANY INFORMATION:
{context}

Generate a response that:

1. **DIRECTLY ADDRESSES** the user's specific question
2. **LEVERAGES CONTEXT** from retrieved company documents
3. **MAINTAINS CONVERSATION FLOW** considering previous exchanges
4. **ADAPTS TONE** based on user intent:
   - Complaint: Empathetic and solution-focused
   - Inquiry: Informative and helpful
   - Request: Action-oriented and clear
   - Compliment: Appreciative and encouraging

5. **PROVIDES ACTIONABLE INFORMATION** when possible
6. **ACKNOWLEDGES LIMITATIONS** if information is incomplete
7. **SUGGESTS NEXT STEPS** when appropriate

RESPONSE STRUCTURE:
- Start with direct answer to the query
- Provide relevant details from company documents
- Include any necessary procedures or steps
- End with helpful follow-up suggestions if needed

Generate a natural, helpful response:
""")
        
        chain = response_prompt | self.llm
        
        try:
            response = chain.invoke({
                "query": query,
                "context": retrieved_context,
                "history_context": history_context,
                "intent": user_intent
            })
            return response.content
        except Exception as e:
            return f"I apologize, but I encountered an error generating a response: {str(e)}"
    
    def generate_faq_from_documents(self, documents: List[Document], num_faqs: int = 10) -> List[Dict[str, str]]:
        """
        Automatically generate FAQs from company documents
        """
        if not documents:
            return []
        
        combined_content = "\n\n".join([doc.page_content for doc in documents[:10]])
        
        if len(combined_content) > 10000:
            combined_content = combined_content[:10000] + "..."
        
        faq_prompt = ChatPromptTemplate.from_template("""
You are an expert at creating customer support FAQs from company documentation.

COMPANY DOCUMENTATION:
{documents}

Generate {num_faqs} high-quality FAQ pairs that:
1. Address common customer questions likely to arise from this documentation
2. Provide clear, actionable answers
3. Cover different aspects of the company's services/products
4. Use customer-friendly language
5. Are specific and helpful

Format each FAQ as:
Q: [Question]
A: [Answer]

Generate diverse FAQs covering different topics from the documentation:
""")
        
        chain = faq_prompt | self.creative_llm
        
        try:
            response = chain.invoke({
                "documents": combined_content,
                "num_faqs": num_faqs
            })
            
            faqs = self._parse_faq_response(response.content)
            return faqs
            
        except Exception as e:
            return [{"question": "Error generating FAQs", "answer": str(e)}]
    
    def generate_response_variations(self, base_response: str, num_variations: int = 3) -> List[str]:
        """
        Generate multiple variations of a response for A/B testing
        """
        variation_prompt = ChatPromptTemplate.from_template("""
You are tasked with creating variations of a customer support response for A/B testing.

ORIGINAL RESPONSE:
{base_response}

Generate {num_variations} different variations that:
1. Maintain the same core information and accuracy
2. Use different phrasing and structure
3. Vary in tone (professional, friendly, concise)
4. Keep the same level of helpfulness
5. Are suitable for customer support context

Variations:
""")
        
        chain = variation_prompt | self.creative_llm
        
        try:
            response = chain.invoke({
                "base_response": base_response,
                "num_variations": num_variations
            })
            
            variations = self._parse_variations(response.content)
            return variations[:num_variations]
            
        except Exception as e:
            return [base_response] 
    
    def generate_follow_up_suggestions(self, query: str, response: str, context: str) -> List[str]:
        """
        Generate intelligent follow-up question suggestions
        """
        followup_prompt = ChatPromptTemplate.from_template("""
Based on this customer support interaction, suggest relevant follow-up questions.

USER QUERY: {query}
ASSISTANT RESPONSE: {response}
CONTEXT: {context}

Generate 3-5 intelligent follow-up questions that:
1. Build naturally on the current conversation
2. Address related topics the customer might want to know
3. Are specific and actionable
4. Help the customer get more value from the support system

Follow-up questions:
""")
        
        chain = followup_prompt | self.creative_llm
        
        try:
            response_obj = chain.invoke({
                "query": query,
                "response": response,
                "context": context[:1000]  
            })
            
            suggestions = self._parse_suggestions(response_obj.content)
            return suggestions
            
        except Exception as e:
            return ["Is there anything else I can help you with?"]
    
    def enhance_query_with_context(self, original_query: str, chat_history: List[Dict]) -> str:
        """
        Enhance user query with conversational context for better retrieval
        """
        if not chat_history:
            return original_query
        
        recent_context = chat_history[-3:] if len(chat_history) > 3 else chat_history
        context_str = "\n".join([
            f"{'User' if msg.get('type') == 'user' else 'Assistant'}: {msg.get('content', '')[:200]}"
            for msg in recent_context
        ])
        
        enhancement_prompt = ChatPromptTemplate.from_template("""
Enhance this user query by adding relevant context from the conversation history.

CONVERSATION HISTORY:
{context}

CURRENT QUERY: {query}

Create an enhanced query that:
1. Maintains the original intent
2. Adds relevant context for better document retrieval
3. Clarifies any ambiguous references
4. Stays concise and focused

Enhanced query:
""")
        
        chain = enhancement_prompt | self.llm
        
        try:
            response = chain.invoke({
                "query": original_query,
                "context": context_str
            })
            
            enhanced = response.content.strip()
            if len(enhanced) > len(original_query) * 3:
                return original_query
            return enhanced
            
        except Exception as e:
            return original_query
    
    def _parse_faq_response(self, response: str) -> List[Dict[str, str]]:
        """Parse FAQ response into structured format"""
        faqs = []
        lines = response.split('\n')
        current_q = ""
        current_a = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_q and current_a:
                    faqs.append({"question": current_q, "answer": current_a})
                current_q = line[2:].strip()
                current_a = ""
            elif line.startswith('A:'):
                current_a = line[2:].strip()
            elif current_a and line:
                current_a += " " + line
        
        if current_q and current_a:
            faqs.append({"question": current_q, "answer": current_a})
        
        return faqs
    
    def _parse_variations(self, response: str) -> List[str]:
        """Parse response variations"""
        lines = response.split('\n')
        variations = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Variation') and not line.startswith('#'):
                clean_line = re.sub(r'^\d+\.\s*', '', line)
                if len(clean_line) > 20: 
                    variations.append(clean_line)
        
        return variations
    
    def _parse_suggestions(self, response: str) -> List[str]:
        """Parse follow-up suggestions"""
        lines = response.split('\n')
        suggestions = []
        
        for line in lines:
            line = line.strip()
            if line and '?' in line:
                clean_line = re.sub(r'^\d+\.\s*', '', line)
                clean_line = re.sub(r'^-\s*', '', clean_line)
                if len(clean_line) > 10:
                    suggestions.append(clean_line)
        
        return suggestions[:5] 

def test_generative_features():
    """Test the generative AI enhancements"""
    enhancer = GenerativeAIEnhancer()
    
    sample_docs = [
        Document(page_content="Company policy states that refunds are processed within 5-7 business days. Customers need to provide original receipt and reason for return."),
        Document(page_content="Our customer service team is available 24/7 through chat, email, and phone support. Response times vary by channel."),
    ]
    
    print("=== Document Summarization ===")
    summary = enhancer.summarize_documents(sample_docs, "How do refunds work?")
    print(summary)
    
    print("\n=== FAQ Generation ===")
    faqs = enhancer.generate_faq_from_documents(sample_docs, 3)
    for faq in faqs:
        print(f"Q: {faq['question']}")
        print(f"A: {faq['answer']}\n")

if __name__ == "__main__":
    test_generative_features()