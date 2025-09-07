import streamlit as st
import requests
import json
import uuid
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Gallery HR Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .sidebar-content {
        padding: 1rem;
    }
    .error-message {
        color: #d32f2f;
        background-color: #ffebee;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .success-message {
        color: #388e3c;
        background-color: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
FASTAPI_URL = "http://localhost:8000"

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'api_status' not in st.session_state:
    st.session_state.api_status = False

# Functions
def check_api_connection():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{FASTAPI_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_query(user_input, session_id):
    """Send query to FastAPI backend"""
    try:
        payload = {
            "session_id": session_id,
            "input": user_input
        }
        response = requests.post(
            f"{FASTAPI_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["answer"], None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the API. Make sure the FastAPI server is running."
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_session_history(session_id):
    """Get chat history from FastAPI backend"""
    try:
        response = requests.get(f"{FASTAPI_URL}/history/{session_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def clear_session_history(session_id):
    """Clear chat history from FastAPI backend"""
    try:
        response = requests.delete(f"{FASTAPI_URL}/history/{session_id}", timeout=10)
        return response.status_code == 200
    except:
        return False

# Sidebar
with st.sidebar:
    st.markdown("<h2 class='sidebar-content'>🤖 Gallery HR Assistant</h2>", unsafe_allow_html=True)
    
    # API Status Check
    if st.button("Check API Status", type="secondary"):
        st.session_state.api_status = check_api_connection()
    
    if st.session_state.api_status:
        st.markdown("<div class='success-message'>✅ API Connected</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='error-message'>❌ API Disconnected</div>", unsafe_allow_html=True)
        st.markdown("**Make sure your FastAPI server is running:**")
        st.code("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
    st.markdown("---")
    
    # Session Info
    st.markdown("**Session Information:**")
    st.text(f"ID: {st.session_state.session_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.chat_history)}")
    
    # Session Controls
    if st.button("🗑️ Clear Chat", type="secondary"):
        if clear_session_history(st.session_state.session_id):
            st.session_state.chat_history = []
            st.success("Chat cleared!")
            st.rerun()
        else:
            st.error("Failed to clear chat history")
    
    if st.button("🔄 New Session", type="secondary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.success("New session started!")
        st.rerun()
    
    st.markdown("---")
    
    # Help section
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Start your FastAPI server** first
        2. **Check API Status** to ensure connection
        3. **Type your question** about Gallery HR or company policies
        4. **Press Enter** or click Send
        5. Use **Clear Chat** to start over
        """)
    
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What is Gallery HR?
        - Tell me about company policies
        - How do I use the Gallery HR system?
        - What are the HR guidelines?
        - Show me the user manual information
        """)

# Main content
st.markdown("<h1 class='main-header'>Gallery HR Assistant Chatbot</h1>", unsafe_allow_html=True)

# Initial API connection check
if not st.session_state.api_status:
    st.session_state.api_status = check_api_connection()

# Chat interface
if st.session_state.api_status:
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong><br>{message['content']}
                    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                        {message['timestamp']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>Assistant:</strong><br>{message['content']}
                    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                        {message['timestamp']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask me anything about Gallery HR:",
                placeholder="Type your question here...",
                key="user_input",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button("Send 📤", type="primary")
        
        # Handle form submission
        if send_button and user_input.strip():
            # Add user message to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({
                'type': 'user',
                'content': user_input,
                'timestamp': timestamp
            })
            
            # Show thinking indicator
            with st.spinner("🤔 Thinking..."):
                # Send query to API
                bot_response, error = send_query(user_input, st.session_state.session_id)
            
            if bot_response:
                # Add bot response to history
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': bot_response,
                    'timestamp': timestamp
                })
                st.success("Response received!")
            else:
                st.error(f"Error: {error}")
            
            # Rerun to update the chat display
            st.rerun()
    
    # Quick action buttons
    st.markdown("---")
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What is Gallery HR?"):
            st.session_state.quick_question = "What is Gallery HR?"
            st.rerun()
    
    with col2:
        if st.button("Company Policies"):
            st.session_state.quick_question = "Tell me about company policies"
            st.rerun()
    
    with col3:
        if st.button("User Manual"):
            st.session_state.quick_question = "Show me user manual information"
            st.rerun()

else:
    # API not connected
    st.error("🚫 Cannot connect to the FastAPI backend")
    st.markdown("""
    **To start the chatbot:**
    
    1. Make sure your FastAPI server is running:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    
    2. Check that the server is accessible at: http://localhost:8000
    
    3. Click "Check API Status" in the sidebar
    """)
    
    if st.button("🔄 Retry Connection", type="primary"):
        st.session_state.api_status = check_api_connection()
        st.rerun()

# Handle quick questions
if hasattr(st.session_state, 'quick_question'):
    user_input = st.session_state.quick_question
    del st.session_state.quick_question
    
    # Add user message
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        'type': 'user',
        'content': user_input,
        'timestamp': timestamp
    })
    
    # Get bot response
    with st.spinner("🤔 Thinking..."):
        bot_response, error = send_query(user_input, st.session_state.session_id)
    
    if bot_response:
        st.session_state.chat_history.append({
            'type': 'bot',
            'content': bot_response,
            'timestamp': timestamp
        })
    
    st.rerun()