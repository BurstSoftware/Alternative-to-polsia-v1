import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(
    page_title="Gemini Agent Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SESSION STATE ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-pro"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "custom_agents" not in st.session_state:
    st.session_state.custom_agents = {}

# ====================== DEFAULT AGENTS ======================
DEFAULT_AGENTS = {
    "🔍 Researcher": {
        "role": "Expert Researcher",
        "goal": "Gather accurate, balanced, and well-sourced information",
        "backstory": "You are a meticulous researcher who values evidence and multiple perspectives.",
        "system_prompt": "You are an expert researcher. Provide detailed, accurate, objective information. Use evidence-based reasoning and present balanced views when appropriate."
    },
    "✍️ Creative Writer": {
        "role": "Creative Writer",
        "goal": "Create engaging, original, and high-quality written content",
        "backstory": "You have a vivid imagination and mastery of storytelling and persuasive writing.",
        "system_prompt": "You are a highly creative writer. Use vivid language, strong narratives, and the appropriate tone for the request. Be original and engaging."
    },
    "💻 Code Expert": {
        "role": "Senior Software Engineer",
        "goal": "Write, debug, review, and explain high-quality code",
        "backstory": "You are a seasoned developer who follows best practices and writes clean, efficient code.",
        "system_prompt": "You are an expert software engineer. Write clean, well-commented code. Always explain your reasoning and suggest improvements."
    },
    "📈 Business Strategist": {
        "role": "Business Strategist",
        "goal": "Provide strategic, data-driven business advice",
        "backstory": "You analyze markets, competition, and opportunities with sharp strategic thinking.",
        "system_prompt": "You are a sharp business strategist. Provide structured, actionable advice with clear reasoning and consideration of risks and opportunities."
    },
    "🧐 Critic & Reviewer": {
        "role": "Constructive Critic",
        "goal": "Give honest, balanced, and helpful feedback",
        "backstory": "You see both strengths and weaknesses and help people improve their work.",
        "system_prompt": "You are a constructive critic. Start with positives, then give specific, actionable feedback. Be honest but encouraging."
    }
}

def get_all_agents():
    return {**DEFAULT_AGENTS, **st.session_state.custom_agents}

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your key at https://aistudio.google.com/app/apikey"
    )
    if api_key:
        st.session_state.api_key = api_key
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            st.error(f"Invalid API Key: {e}")

    st.session_state.model_name = st.selectbox(
        "Model",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
        index=1
    )

    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.temperature, 0.05,
        help="Higher = more creative, Lower = more deterministic"
    )

    st.divider()
    if st.button("🗑️ Clear All Chat Histories"):
        st.session_state.chat_histories = {}
        st.rerun()

# ====================== MAIN APP ======================
st.title("🤖 Gemini Agent Studio")
st.markdown("### Multi-Agent Interface powered by Google Gemini")

if not st.session_state.api_key:
    st.warning("Please enter your Google Gemini API Key in the sidebar to continue.")
    st.stop()

all_agents = get_all_agents()

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs([
    "📚 Agent Library", 
    "💬 Chat with Agent", 
    "🤝 Multi-Agent Crew", 
    "➕ Create Custom Agent"
])

# --- TAB 1: Agent Library ---
with tab1:
    st.header("Available Agents")
    cols = st.columns(3)
    
    for idx, (name, info) in enumerate(all_agents.items()):
        with cols[idx % 3]:
            with st.container(border=True):
                st.subheader(name)
                st.markdown(f"**Role:** {info['role']}")
                st.markdown(f"**Goal:** {info['goal']}")
                with st.expander("Backstory"):
                    st.write(info['backstory'])
                if st.button(f"Chat with this agent", key=f"chat_btn_{name}"):
                    st.session_state.selected_agent = name
                    st.info("→ Switch to the **Chat with Agent** tab")

# --- TAB 2: Single Agent Chat ---
with tab2:
    st.header("💬 Chat with a Single Agent")
    
    agent_names = list(all_agents.keys())
    
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = agent_names[0]
    
    selected_agent = st.selectbox(
        "Choose your agent",
        agent_names,
        index=agent_names.index(st.session_state.selected_agent) if st.session_state.selected_agent in agent_names else 0
    )
    st.session_state.selected_agent = selected_agent
    
    agent_info = all_agents[selected_agent]
    
    with st.expander("Agent Info"):
        st.write(f"**Role:** {agent_info['role']}")
        st.write(f"**Goal:** {agent_info['goal']}")
        st.write(agent_info['backstory'])
    
    # Initialize history
    if selected_agent not in st.session_state.chat_histories:
        st.session_state.chat_histories[selected_agent] = []
    
    history = st.session_state.chat_histories[selected_agent]
    
    # Display messages
    for msg in history:
        role = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input(f"Message {selected_agent}..."):
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner(f"{selected_agent} is thinking..."):
                try:
                    model = genai.GenerativeModel(
                        model_name=st.session_state.model_name,
                        system_instruction=agent_info["system_prompt"],
                        generation_config=genai.GenerationConfig(
                            temperature=st.session_state.temperature
                        )
                    )
                    
                    gemini_history = [
                        {"role": m["role"], "parts": [m["content"]]} 
                        for m in history[:-1]
                    ]
                    
                    chat = model.start_chat(history=gemini_history)
                    response = chat.send_message(prompt)
                    reply = response.text
                    
                    st.markdown(reply)
                    history.append({"role": "model", "content": reply})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# --- TAB 3: Multi-Agent Crew (The Cool Part) ---
with tab3:
    st.header("🤝 Multi-Agent Crew")
    st.markdown("Give one task to multiple agents. They collaborate sequentially and deliver a final synthesized result.")
    
    task = st.text_area(
        "Task for the team",
        placeholder="Example: Research current trends in AI agents, write a blog post about it, then review and improve the post.",
        height=100
    )
    
    selected_team = st.multiselect(
        "Select agents for the crew (order = execution order)",
        options=agent_names,
        default=agent_names[:3]
    )
    
    if st.button("🚀 Launch Crew", type="primary", disabled=not task or len(selected_team) == 0):
        progress = st.progress(0)
        full_context = f"**Task:** {task}\n\n"
        
        for i, agent_name in enumerate(selected_team):
            progress.progress((i) / len(selected_team))
            agent_info = all_agents[agent_name]
            
            st.write(f"**{agent_name}** is working...")
            
            prompt = f"""Task: {task}

Previous work:
{full_context}

You are the {agent_info['role']}. {agent_info['goal']}.
Provide your best contribution to help complete the task."""

            try:
                model = genai.GenerativeModel(
                    model_name=st.session_state.model_name,
                    system_instruction=agent_info["system_prompt"],
                    generation_config=genai.GenerationConfig(
                        temperature=st.session_state.temperature
                    )
                )
                response = model.generate_content(prompt)
                output = response.text
                
                with st.expander(f"✅ {agent_name}'s Output", expanded=True):
                    st.markdown(output)
                
                full_context += f"\n\n**{agent_name}:**\n{output}"
                time.sleep(0.6)
                
            except Exception as e:
                st.error(f"Error with {agent_name}: {e}")
                break
        
        progress.progress(1.0)w
        
        # Final synthesis
        st.subheader("📋 Final Team Deliverable")
        try:
            manager = genai.GenerativeModel(
                model_name=st.session_state.model_name,
                generation_config=genai.GenerationConfig(temperature=0.4)
            )
            
            final_prompt = f"""Synthesize the following team contributions into one polished, complete final answer for the original task.

Original Task: {task}

Team Contributions:
{full_context}

Create a high-quality, well-structured final output."""
            
            final = manager.generate_content(final_prompt).text
            st.markdown(final)
            
            st.download_button(
                "📥 Download Final Output",
                data=final,
                file_name="crew_output.md"
            )
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

# --- TAB 4: Create Custom Agent ---
with tab4:
    st.header("Create Your Own Agent")
    
    with st.form("custom_agent"):
        name = st.text_input("Agent Name (add emoji for style)")
        role = st.text_input("Role")
        goal = st.text_area("Goal")
        backstory = st.text_area("Backstory (optional)")
        system_prompt = st.text_area("System Prompt (most important)", height=150)
        
        if st.form_submit_button("➕ Create Agent"):
            if name and role and goal and system_prompt:
                st.session_state.custom_agents[name] = {
                    "role": role,
                    "goal": goal,
                    "backstory": backstory,
                    "system_prompt": system_prompt
                }
                st.success(f"Agent **{name}** created successfully!")
                st.balloons()
            else:
                st.error("Please fill Name, Role, Goal and System Prompt")

st.divider()
st.caption("Made with Streamlit + Google Gemini API • Works with both free and paid keys")
