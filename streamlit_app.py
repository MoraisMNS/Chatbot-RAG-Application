# enhanced_streamlit_app.py
import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
import time

# Page configuration
st.set_page_config(
    page_title="Customer support Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS with clean modern design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .app-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Status Bar */
    .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: #64748b;
    }
    
    .status-connected {
        color: #10b981;
        font-weight: 500;
    }
    
    .status-disconnected {
        color: #ef4444;
        font-weight: 500;
    }
    
    /* Chat Container */
    .chat-container {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        min-height: 2px;
        margin-bottom: 1rem;
        overflow: hidden;
    }
    
    .chat-header {
        background: #f8fafc;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #e2e8f0;
        font-weight: 600;
        color: #334155;
        font-size: 0.875rem;
    }
    
    .chat-messages {
        padding: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .message {
        margin: 0 1.5rem 1.5rem;
        display: flex;
        gap: 1rem;
    }
    
    .message-user {
        flex-direction: row-reverse;
    }
    
    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    
    .avatar-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .avatar-bot {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .message-content {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        max-width: 70%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .message-user .message-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    .message-timestamp {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    .message-user .message-timestamp {
        color: rgba(255,255,255,0.8);
    }
    
    /* Enhanced Features */
    .enhanced-feature {
        margin-top: 1rem;
        padding: 1rem;
        background: #f0f9ff;
        border: 1px solid #e0f2fe;
        border-radius: 8px;
        border-left: 4px solid #0ea5e9;
    }
    
    .feature-title {
        font-weight: 600;
        color: #0369a1;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-content {
        font-size: 0.875rem;
        color: #374151;
        line-height: 1.5;
    }
    
    /* Follow-up Suggestions */
    .followup-suggestions {
        margin-top: 1rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .followup-btn {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #475569;
        padding: 0.5rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        display: inline-block;
    }
    
    .followup-btn:hover {
        background: #e2e8f0;
        border-color: #94a3b8;
    }
    
    /* Input Section */
    .input-section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .input-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .input-title {
        font-weight: 600;
        color: #334155;
        font-size: 0.875rem;
    }
    
    .feature-toggles {
        display: flex;
        gap: 1rem;
        font-size: 0.75rem;
    }
    
    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.75rem;
        margin-top: 1.5rem;
    }
    
    .quick-action-btn {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    
    .quick-action-btn:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Sidebar Styles */
    .sidebar-section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .sidebar-title {
        font-weight: 600;
        color: #334155;
        font-size: 0.875rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Analytics Cards */
    .analytics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0369a1;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* FAQ Section */
    .faq-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        overflow: hidden;
    }
    
    .faq-question {
        background: #f8fafc;
        padding: 0.75rem 1rem;
        font-weight: 500;
        color: #334155;
        font-size: 0.875rem;
        cursor: pointer;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .faq-answer {
        padding: 1rem;
        font-size: 0.875rem;
        color: #64748b;
        line-height: 1.5;
    }
    
    /* Loading States */
    .loading-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 2rem;
        color: #64748b;
        font-size: 0.875rem;
    }
    
    /* Error States */
    .error-message {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #16a34a;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        margin: 0.5rem 0;
    }
    
    /* AI Comparison Section */
    .comparison-tabs {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .tab-content {
        padding: 1.5rem;
    }
    
    .approach-header {
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }
    
    .approach-response {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.875rem;
        color: #374151;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .status-bar {
            flex-direction: column;
            gap: 0.5rem;
            align-items: flex-start;
        }
        
        .message-content {
            max-width: 90%;
        }
        
        .quick-actions {
            grid-template-columns: 1fr;
        }
        
        .analytics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    /* Button Overrides */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Form Input Overrides */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 0.875rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Checkbox and Toggle Overrides */
    .stCheckbox {
        font-size: 0.75rem;
    }
    
    /* Tab Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
FASTAPI_URL = "http://127.0.0.1:8000"

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'api_status' not in st.session_state:
    st.session_state.api_status = False

if 'use_enhanced_features' not in st.session_state:
    st.session_state.use_enhanced_features = True

if 'show_analytics' not in st.session_state:
    st.session_state.show_analytics = False

# Functions (keeping all existing functions unchanged)
def check_api_connection():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{FASTAPI_URL}/", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else {}
    except:
        return False, {}

def send_enhanced_query(user_input: str, session_id: str, use_enhancements: bool = True) -> Dict[str, Any]:
    """Send enhanced query to FastAPI backend"""
    try:
        if use_enhancements:
            payload = {
                "session_id": session_id,
                "input": user_input,
                "use_summarization": True,
                "generate_followups": True,
                "response_style": "professional"
            }
            
            response = requests.post(
                f"{FASTAPI_URL}/query/enhanced",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=45
            )
        else:
            payload = {
                "session_id": session_id,
                "input": user_input,
                "use_enhancements": False
            }
            
            response = requests.post(
                f"{FASTAPI_URL}/query",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the API. Make sure the FastAPI server is running."
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_usage_stats():
    """Get usage statistics from API"""
    try:
        response = requests.get(f"{FASTAPI_URL}/stats/usage", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def generate_faqs(num_faqs: int = 10):
    """Generate FAQs from API"""
    try:
        response = requests.post(
            f"{FASTAPI_URL}/generate-faqs",
            json={"num_faqs": num_faqs},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def analyze_documents():
    """Analyze documents from API"""
    try:
        response = requests.get(f"{FASTAPI_URL}/analyze/documents", timeout=60)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def test_ai_approaches(query: str):
    """Test different AI approaches"""
    try:
        response = requests.post(
            f"{FASTAPI_URL}/test/ai-approaches",
            params={"query": query, "session_id": st.session_state.session_id},
            timeout=90
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Check API status on load
if 'initial_check' not in st.session_state:
    st.session_state.api_status, _ = check_api_connection()
    st.session_state.initial_check = True

# Main Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">💬 Customer support Chatbot</h1>
    <p class="app-subtitle">Chatbot that pulls answers from company internal documentation</p>
</div>
""", unsafe_allow_html=True)

# Status Bar
status_emoji = "🟢" if st.session_state.api_status else "🔴"
status_text = "Connected" if st.session_state.api_status else "Disconnected"
status_class = "status-connected" if st.session_state.api_status else "status-disconnected"

st.markdown(f"""
<div class="status-bar">
    <div class="status-item">
        <span>API Status:</span>
        <span class="{status_class}">{status_emoji} {status_text}</span>
    </div>
    <div class="status-item">
        <span>Session:</span>
        <span>{st.session_state.session_id[:8]}...</span>
    </div>
    <div class="status-item">
        <span>Messages:</span>
        <span>{len(st.session_state.chat_history)}</span>
    </div>
    <div class="status-item">
        <span>Enhanced Features:</span>
        <span>{"✅ Enabled" if st.session_state.use_enhanced_features else "❌ Disabled"}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content Area
col_main, col_sidebar = st.columns([3, 1])

with col_main:
    # Chat Container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="chat-header">💬 Conversation</div>', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        for i, message in enumerate(st.session_state.chat_history):
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="message message-user">
                    <div class="message-content">
                        {message['content']}
                        <div class="message-timestamp">{message['timestamp']}</div>
                    </div>
                    <div class="message-avatar avatar-user">👤</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message">
                    <div class="message-avatar avatar-bot">🤖</div>
                    <div class="message-content">
                        {message['content']}
                        <div class="message-timestamp">{message['timestamp']}</div>
                """, unsafe_allow_html=True)
                
                # Enhanced features display
                if 'enhanced_features' in message:
                    features = message['enhanced_features']
                    
                    if features.get('document_summary'):
                        st.markdown(f"""
                        <div class="enhanced-feature">
                            <div class="feature-title">📄 Document Summary</div>
                            <div class="feature-content">{features['document_summary']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if features.get('follow_up_suggestions'):
                        suggestions_html = ""
                        for j, suggestion in enumerate(features['follow_up_suggestions'][:3]):
                            button_key = f"followup_{i}_{j}_{hash(suggestion)}"
                            if st.button(f"💡 {suggestion}", key=button_key):
                                st.session_state.quick_question = suggestion
                                st.rerun()
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="loading-indicator">
            <span>👋</span>
            <span>Hello! Ask me anything about your company or documents.</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input Section
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("""
    <div class="input-header">
        <div class="input-title">✍️ Ask a question</div>
        <div class="feature-toggles">
            <label>Advanced AI features available</label>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.api_status:
        with st.form(key="chat_form", clear_on_submit=True):
            col_input, col_send = st.columns([4, 1])
            
            with col_input:
                user_input = st.text_input(
                    "Message",
                    placeholder="Type your question here...",
                    key="user_input",
                    label_visibility="collapsed"
                )
            
            with col_send:
                send_button = st.form_submit_button("Send", type="primary")
            
            # Advanced Options
            col1, col2, col3 = st.columns(3)
            with col1:
                use_enhancements = st.checkbox("🔮 Enhanced AI", value=st.session_state.use_enhanced_features)
            with col2:
                show_processing = st.checkbox("⚡ Show Progress", value=True)
            with col3:
                generate_followups = st.checkbox("💡 Suggestions", value=True)
            
            # Handle form submission
            if send_button and user_input.strip():
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Add user message
                st.session_state.chat_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': timestamp
                })
                
                # Show processing
                if show_processing:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, status in enumerate([
                        "🔍 Analyzing query...",
                        "📚 Retrieving documents...", 
                        "🧠 Generating response...",
                        "✨ Applying enhancements...",
                        "✅ Complete!"
                    ]):
                        status_text.text(status)
                        progress_bar.progress((i + 1) * 20)
                        time.sleep(0.3)
                    
                    status_text.empty()
                    progress_bar.empty()
                else:
                    with st.spinner("🤖 Thinking..."):
                        time.sleep(0.5)
                
                # Send query
                result, error = send_enhanced_query(
                    user_input, 
                    st.session_state.session_id, 
                    use_enhancements
                )
                
                if result:
                    bot_message = {
                        'type': 'bot',
                        'content': result.get("answer", ""),
                        'timestamp': timestamp
                    }
                    
                    if use_enhancements and 'enhanced_features' in result:
                        bot_message['enhanced_features'] = result['enhanced_features']
                    
                    if 'metadata' in result:
                        bot_message['metadata'] = result['metadata']
                    
                    st.session_state.chat_history.append(bot_message)
                    st.success("✅ Response received!")
                else:
                    st.markdown(f'<div class="error-message">❌ {error}</div>', unsafe_allow_html=True)
                
                st.rerun()
    
    else:
        st.markdown("""
        <div class="error-message">
            ❌ API connection required. Please start the FastAPI server and refresh the page.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions
    if st.session_state.api_status:
        st.markdown("### 🚀 Quick Questions")
        
        quick_questions = [
            "What is this document about?",
            "Tell me about company policies", 
            "Show me company products",
            "How can I get support?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(quick_questions):
            with cols[i % 2]:
                if st.button(question, key=f"quick_{i}"):
                    st.session_state.quick_question = question
                    st.rerun()

with col_sidebar:
    # Session Controls
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">🎛️ Session Controls</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.success("Chat cleared!")
            st.rerun()
    
    with col_b:
        if st.button("🔄 New Session", type="secondary"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.chat_history = []
            st.success("New session started!")
            st.rerun()
    
    # API Controls
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">🔧 System Controls</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Check API Status"):
        st.session_state.api_status, api_info = check_api_connection()
        if api_info:
            st.session_state.api_info = api_info
        st.rerun()
    
    # Enhanced Features Toggle
    st.session_state.use_enhanced_features = st.toggle(
        "Enhanced AI Features", 
        value=st.session_state.use_enhanced_features
    )
    
    # Analytics
    if st.session_state.api_status:
        with st.expander("📊 Analytics", expanded=False):
            if st.button("📈 Show Dashboard"):
                st.session_state.show_analytics = not st.session_state.show_analytics
            
            if st.button("🔄 Generate FAQs"):
                with st.spinner("Generating FAQs..."):
                    faq_result = generate_faqs(8)
                    if faq_result:
                        st.session_state.generated_faqs = faq_result
                        st.success("FAQs generated!")
            
            if st.button("📋 Analyze Documents"):
                with st.spinner("Analyzing documents..."):
                    analysis = analyze_documents()
                    if analysis:
                        st.session_state.document_analysis = analysis
                        st.success("Analysis complete!")
        
        with st.expander("📁 Documents", expanded=False):
            uploaded = st.file_uploader("Upload PDF", type=["pdf"])
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📤 Index", disabled=not uploaded):
                    if uploaded and st.session_state.api_status:
                        try:
                            response = requests.post(
                                f"{FASTAPI_URL}/ingest/file",
                                params={"sync": True},
                                files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
                            )
                            st.success("✅ Indexed!")
                        except:
                            st.error("❌ Index failed")
            
            with col_b:
                if st.button("🔄 Reindex"):
                    if st.session_state.api_status:
                        try:
                            requests.post(f"{FASTAPI_URL}/ingest/folder")
                            st.success("✅ Reindexing started!")
                        except:
                            st.error("❌ Failed")
        
        with st.expander("🧪 AI Testing", expanded=False):
            if st.button("🔬 Test AI Approaches"):
                st.session_state.show_ai_test = True

if st.session_state.show_analytics and st.session_state.api_status:
    st.markdown("---")
    st.markdown("### 📊 Analytics Dashboard")
    
    stats = get_usage_stats()
    if stats:
        st.markdown('<div class="analytics-grid">', unsafe_allow_html=True)
        
        metrics = [
            ("Total Sessions", stats.get('total_sessions', 0)),
            ("Active Sessions", stats.get('active_sessions', 0)),
            ("Total Messages", stats.get('total_messages', 0)),
            ("Avg Messages/Session", f"{stats.get('average_messages_per_session', 0):.1f}")
        ]
        
        for label, value in metrics:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


if hasattr(st.session_state, 'generated_faqs') and st.session_state.generated_faqs:
    st.markdown("---")
    st.markdown("### 🤖 AI-Generated FAQs")

    payload = st.session_state.generated_faqs

    faqs = []
    if isinstance(payload, list):
        faqs = payload
    elif isinstance(payload, dict):
        faqs = (
            payload.get("faqs")
            or payload.get("results")
            or payload.get("items")
            or (payload.get("data") or {}).get("faqs")
            or []
        )

    if not faqs:
        st.info("No FAQs returned by the API (payload keys not recognized).")
    else:
        for faq in faqs:
            q = faq.get("question") if isinstance(faq, dict) else str(faq)
            a = faq.get("answer") if isinstance(faq, dict) else ""
            with st.expander(f"❓ {q}", expanded=False):
                st.markdown(f'<div class="faq-answer">{a}</div>', unsafe_allow_html=True)



if hasattr(st.session_state, 'document_analysis') and st.session_state.document_analysis:
    st.markdown("---")
    st.markdown("### 📄 Document Analysis")
    
    analysis = st.session_state.document_analysis.get('analysis', {})
    
    if 'overall_summary' in analysis:
        st.markdown("#### 📋 Overall Summary")
        st.markdown(f'<div class="approach-response">{analysis["overall_summary"]}</div>', 
                   unsafe_allow_html=True)
    
    if 'generated_faqs' in analysis:
        st.markdown("#### ❓ Key Questions from Documents")
        for faq in analysis['generated_faqs'][:3]:
            st.markdown(f"**Q:** {faq['question']}")
            st.markdown(f"**A:** {faq['answer']}")
            st.markdown("---")


if hasattr(st.session_state, 'show_ai_test') and st.session_state.show_ai_test:
    st.markdown("---")
    st.markdown("### 🧪 AI Approaches Comparison")
    
    with st.form("ai_test_form"):
        test_query = st.text_input("Enter a test query:", value="What are the company policies?")
        test_button = st.form_submit_button("🔬 Test All Approaches")
        
        if test_button and test_query:
            with st.spinner("Testing different AI approaches..."):
                test_results = test_ai_approaches(test_query)
                
                if test_results:
                    st.success("✅ Comparison complete!")
                    
                    approaches = test_results.get('results', {})
                    tab_names = list(approaches.keys())
                    
                    if tab_names:
                        tabs = st.tabs([name.replace('_', ' ').title() for name in tab_names])
                        
                        for i, (approach_name, approach_data) in enumerate(approaches.items()):
                            with tabs[i]:
                                st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                                
                                if 'error' in approach_data:
                                    st.markdown(f'<div class="error-message">❌ Error: {approach_data["error"]}</div>', 
                                              unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div class="approach-header">Approach: {approach_data.get("approach", "Unknown")}</div>', 
                                              unsafe_allow_html=True)
                                    st.markdown("**Response:**")
                                    st.markdown(f'<div class="approach-response">{approach_data.get("answer", "No response")}</div>', 
                                              unsafe_allow_html=True)
                                    
                                    if 'features' in approach_data:
                                        st.markdown("**Enhanced Features:**")
                                        features = approach_data['features']
                                        
                                        if 'document_summary' in features:
                                            st.markdown("*Document Summary:*")
                                            st.text_area("Summary", features['document_summary'], height=100)
                                        
                                        if 'follow_up_suggestions' in features:
                                            st.markdown("*Follow-up Suggestions:*")
                                            for suggestion in features['follow_up_suggestions']:
                                                st.markdown(f"• {suggestion}")
                                    
                                    if 'metadata' in approach_data:
                                        with st.expander("Technical Details"):
                                            st.json(approach_data['metadata'])
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-message">❌ Failed to test approaches</div>', 
                              unsafe_allow_html=True)
    
    if st.button("❌ Close Test"):
        del st.session_state.show_ai_test
        st.rerun()

if hasattr(st.session_state, 'quick_question'):
    user_input = st.session_state.quick_question
    del st.session_state.quick_question
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        'type': 'user',
        'content': user_input,
        'timestamp': timestamp
    })
    
    with st.spinner("🤖 Processing with Enhanced AI..."):
        result, error = send_enhanced_query(
            user_input, 
            st.session_state.session_id, 
            st.session_state.use_enhanced_features
        )
    
    if result:
        bot_message = {
            'type': 'bot',
            'content': result.get("answer", ""),
            'timestamp': timestamp
        }
        
        if st.session_state.use_enhanced_features and 'enhanced_features' in result:
            bot_message['enhanced_features'] = result['enhanced_features']
        
        st.session_state.chat_history.append(bot_message)
    
    st.rerun()

if st.session_state.api_status and len(st.session_state.chat_history) > 0:
    with col_sidebar:
        with st.expander("⚡ Performance", expanded=False):
            last_message = st.session_state.chat_history[-1] if st.session_state.chat_history else None
            
            if last_message and 'metadata' in last_message:
                metadata = last_message['metadata']
                
                if 'processing_time' in metadata:
                    st.metric("Response Time", f"{metadata['processing_time']:.2f}s")
                
                if 'documents_retrieved' in metadata:
                    st.metric("Documents Retrieved", metadata['documents_retrieved'])
                
                if 'enhancement_used' in metadata:
                    status = "✨ Enhanced" if metadata['enhancement_used'] else "Basic"
                    st.markdown(f"**AI Mode:** {status}")

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #64748b; background: #f8fafc; border-radius: 8px; margin-top: 2rem;'>
    <h4 style='color: #334155; margin-bottom: 1rem;'>💬 Customer support Chatbot v2.0</h4>
    <p style='margin-bottom: 1rem; font-size: 0.875rem;'>
        <span style='background: #e0f2fe; color: #0369a1; padding: 0.25rem 0.5rem; border-radius: 12px; margin: 0.25rem; font-size: 0.75rem;'>Document Analysis</span>
        <span style='background: #f0f9ff; color: #0284c7; padding: 0.25rem 0.5rem; border-radius: 12px; margin: 0.25rem; font-size: 0.75rem;'>Intent Detection</span>
        <span style='background: #ecfdf5; color: #059669; padding: 0.25rem 0.5rem; border-radius: 12px; margin: 0.25rem; font-size: 0.75rem;'>Smart Suggestions</span>
        <span style='background: #fef3c7; color: #d97706; padding: 0.25rem 0.5rem; border-radius: 12px; margin: 0.25rem; font-size: 0.75rem;'>Response Enhancement</span>
    </p>
    <p style='font-size: 0.75rem; margin: 0;'><em>Powered by Advanced Generative AI & RAG Technology</em></p>
</div>
""", unsafe_allow_html=True)

if 'last_api_check' not in st.session_state:
    st.session_state.last_api_check = time.time()

if time.time() - st.session_state.last_api_check > 60:
    st.session_state.api_status, _ = check_api_connection()
    st.session_state.last_api_check = time.time()