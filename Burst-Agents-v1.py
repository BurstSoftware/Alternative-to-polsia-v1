import streamlit as st
import time
from openai import OpenAI

st.set_page_config(
    page_title="NVIDIA NIM Agent Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS (Grok-inspired) ======================
st.markdown("""
<style>
    /* Main dark theme */
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Message bubbles */
    .stChatMessage {
        padding: 12px 16px;
        border-radius: 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    /* User message */
    div[data-testid="stChatMessage"][data-chat-message-user="true"] {
        background-color: #1e88e5;
        color: white;
        margin-left: 15%;
        border-bottom-right-radius: 4px;
    }
    
    /* Assistant message */
    div[data-testid="stChatMessage"]:not([data-chat-message-user="true"]) {
        background-color: #262730;
        border: 1px solid #3a3d4a;
        margin-right: 15%;
        border-bottom-left-radius: 4px;
    }
    
    /* Avatars */
    .stChatMessage img {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50%;
        box-shadow: 0 0 12px rgba(255,255,255,0.1);
    }
    
    /* Header */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7b4cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg, section[data-testid="stSidebar"] {
        background-color: #161925;
    }
    
    /* Input box */
    .stChatInput {
        border-radius: 20px !important;
        border: 1px solid #3a3d4a;
    }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
# ... (keep your other session state variables)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Agent Studio")
    st.markdown("**NVIDIA NIM** • Powered by Grok-style UI")
    
    api_key = st.text_input("NVIDIA NIM API Key", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key

    # Model & Settings (keep your existing code)
    st.divider()
    # ... your model selectbox, temperature, etc.

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.current_chat = []
        st.rerun()

# ====================== MAIN CHAT ======================
st.markdown('<h1 class="main-header">🤖 NVIDIA NIM Agent Studio</h1>', unsafe_allow_html=True)

# Agent selector
agents = get_all_agents()
selected_agent_name = st.selectbox("🎭 Select Agent", list(agents.keys()), index=0)
st.session_state.selected_agent = agents[selected_agent_name]

st.caption(f"**Active Agent:** {selected_agent_name} | **Model:** {st.session_state.model_name}")

# Chat Container
chat_container = st.container()

with chat_container:
    for msg in st.session_state.current_chat:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💼"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask anything..."):
    # Add user message
    st.session_state.current_chat.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Thinking..."):
            response = generate_response(prompt, st.session_state.selected_agent)
            
            if response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                st.session_state.current_chat.append({"role": "assistant", "content": full_response})
            else:
                st.error("Failed to get response")
