import streamlit as st
from openai import OpenAI
import time

st.set_page_config(
    page_title="NVIDIA NIM Agent Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SESSION STATE ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = "meta/llama-3.1-70b-instruct"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "custom_agents" not in st.session_state:
    st.session_state.custom_agents = {}
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

# ====================== DEFAULT AGENTS ======================
DEFAULT_AGENTS = {
    "🔍 Researcher": {"role": "Expert Researcher", "goal": "Gather accurate, balanced, and well-sourced information",
                     "backstory": "You are a meticulous researcher who values evidence and multiple perspectives.",
                     "system_prompt": "You are an expert researcher. Provide detailed, accurate, objective information. Use evidence-based reasoning and present balanced views when appropriate."},
    "✍️ Creative Writer": {"role": "Creative Writer", "goal": "Create engaging, original, and high-quality written content",
                           "backstory": "You have a vivid imagination and mastery of storytelling and persuasive writing.",
                           "system_prompt": "You are a highly creative writer. Use vivid language, strong narratives, and the appropriate tone for the request. Be original and engaging."},
    "💻 Code Expert": {"role": "Senior Software Engineer", "goal": "Write, debug, review, and explain high-quality code",
                       "backstory": "You are a seasoned developer who follows best practices and writes clean, efficient code.",
                       "system_prompt": "You are an expert software engineer. Write clean, well-commented code. Always explain your reasoning and suggest improvements."},
    "📈 Business Strategist": {"role": "Business Strategist", "goal": "Provide strategic, data-driven business advice",
                               "backstory": "You analyze markets, competition, and opportunities with sharp strategic thinking.",
                               "system_prompt": "You are a sharp business strategist. Provide structured, actionable advice with clear reasoning and consideration of risks and opportunities."},
    "🧐 Critic & Reviewer": {"role": "Constructive Critic", "goal": "Give honest, balanced, and helpful feedback",
                             "backstory": "You see both strengths and weaknesses and help people improve their work.",
                             "system_prompt": "You are a constructive critic. Start with positives, then give specific, actionable feedback. Be honest but encouraging."}
}

def get_all_agents():
    return {**DEFAULT_AGENTS, **st.session_state.custom_agents}

# ====================== NVIDIA CLIENT ======================
def get_nvidia_client():
    """Returns OpenAI client configured for NVIDIA NIM"""
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your NVIDIA NIM API Key in the sidebar to continue.")
        return None
    try:
        return OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=st.session_state.api_key
        )
    except Exception as e:
        st.error(f"Client Error: {e}")
        return None

# ====================== GENERATE RESPONSE ======================
def generate_response(prompt, agent=None):
    client = get_nvidia_client()
    if not client:
        return None
    
    messages = []
    
    # Add agent system prompt
    if agent and agent.get("system_prompt"):
        messages.append({"role": "system", "content": agent["system_prompt"]})
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=st.session_state.model_name,
            messages=messages,
            temperature=st.session_state.temperature,
            max_tokens=4096,
            stream=True
        )
        return response
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_key = st.text_input(
        "NVIDIA NIM API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your free key → https://build.nvidia.com/",
        placeholder="nvapi-..."
    )
    
    if api_key:
        st.session_state.api_key = api_key

    # Model Selection
    nvidia_models = [
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "nvidia/nemotron-4-340b-instruct",
        "deepseek-ai/deepseek-v3",
        "qwen/qwen2.5-72b-instruct",
        "mistralai/mistral-large",
        "google/gemma-2-27b-it",
    ]
    
    st.session_state.model_name = st.selectbox(
        "NVIDIA Model", nvidia_models, index=0
    )

    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.temperature, 0.05
    )

    st.divider()
    if st.button("🗑️ Clear All Chat Histories"):
        st.session_state.chat_histories = {}
        st.rerun()

    st.caption("Powered by NVIDIA NIM • Free Tier")

# ====================== MAIN APP ======================
st.title("🤖 NVIDIA NIM Agent Studio")

# Agent Selection
agents = get_all_agents()
agent_names = list(agents.keys())
selected_agent_name = st.selectbox("Select Agent", agent_names, index=0)
st.session_state.selected_agent = agents[selected_agent_name]

st.info(f"**Active Agent:** {selected_agent_name} | **Model:** {st.session_state.model_name}")

# Chat Interface
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

for msg in st.session_state.current_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.current_chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        response = generate_response(prompt, st.session_state.selected_agent)
        
        if response:
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            # Save to history
            st.session_state.current_chat.append({"role": "assistant", "content": full_response})
        else:
            st.warning("Could not get response. Please check your API key.")
