import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler
from src.graph import build_support_graph

load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="SupportDesk AI | Multi-Agent", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium UI ---
st.markdown("""
<style>
    /* Main Background adjustments */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Custom Header Styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    /* Subtitle Styling */
    .sub-header {
        color: #9CA3AF;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        color: #38BDF8;
    }
    
    /* Red alert tweak */
    .stAlert {
        border-radius: 10px;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 4px;
    }
    .badge-green {
        background-color: #13231c;
        color: #34D399;
        border: 1px solid #065F46;
    }
    .badge-blue {
        background-color: #1e293b;
        color: #38BDF8;
        border: 1px solid #1E40AF;
    }
</style>
""", unsafe_allow_html=True)

# --- Graph Initialization ---
@st.cache_resource
def get_graph():
    return build_support_graph()

app = get_graph()

# --- Session State Management ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "awaiting_approval" not in st.session_state:
    st.session_state.awaiting_approval = False

config = {
    "configurable": {"thread_id": st.session_state.thread_id},
    "callbacks": [CallbackHandler()]
}

# --- Sidebar Controls ---
# --- Sidebar Navigation & Diagnostics ---
with st.sidebar:
    st.title("⚡ Control Panel")
    st.markdown("---")
    
    st.markdown("**Engine Status**")
    st.markdown('<span class="status-badge badge-green">● Active Nodes Online</span>', unsafe_allow_html=True)
    st.markdown('<span class="status-badge badge-blue">Model: gemini-3.6-flash</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Session Configuration**")
    st.code(f"Thread ID: {st.session_state.thread_id}", language="text")
    
    if st.button("Reset Conversation", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.awaiting_approval = False
        st.rerun()

# --- Main App Header ---
st.markdown('<div class="main-header">⚡ SupportDesk AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Multi-Agent Customer Support System with Human-in-the-Loop Approval</div>', unsafe_allow_html=True)

# Top Metrics Row
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="Active Agents", value="Router, Billing, Tech, General")
with col_m2:
    st.metric(label="Human Guardrail", value="Active (Billing)")
with col_m3:
    st.metric(label="Messages", value=len(st.session_state.messages))

st.markdown("---")

# --- Utility Functions ---
def get_clean_string(msg_obj):
    if isinstance(msg_obj, dict):
        val = msg_obj.get("content", "")
    elif hasattr(msg_obj, "content"):
        val = msg_obj.content
    else:
        val = msg_obj

    if isinstance(val, dict):
        return val.get("text", str(val))
    elif isinstance(val, list) and len(val) > 0:
        first = val[0]
        if isinstance(first, dict):
            return first.get("text", str(first))
        return str(first)
        
    return str(val)

# --- Chat Rendering ---
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "👤" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.write(msg["content"])

# --- User Input Handling ---
user_query = st.chat_input("Type your query (e.g., 'I was charged twice. Refund me!')...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.write(user_query)

    initial_state = {
        "messages": [{"role": "user", "content": user_query}],
        "category": "",
        "requires_human_approval": False,
        "resolution": ""
    }

    try:
        with st.spinner("🤖 Multi-agent graph orchestrating response..."):
            events = app.stream(initial_state, config, stream_mode="values")
            for event in events:
                pass

        snapshot = app.get_state(config)
        
        if snapshot.next and "billing_agent" in snapshot.next:
            st.session_state.awaiting_approval = True
            st.rerun()
        else:
            state_data = snapshot.values
            if "messages" in state_data and state_data["messages"]:
                last_msg = state_data["messages"][-1]
                text = get_clean_string(last_msg)
                st.session_state.messages.append({"role": "assistant", "content": text})
                st.rerun()

    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            st.error("⏳ **Rate Limit Hit!** Free-tier quota exceeded. Please wait ~30 seconds before sending another query.")
        else:
            st.error(f"Error during graph execution: {e}")

# --- HITL Interruption UI Section ---
if st.session_state.awaiting_approval:
    st.markdown("---")
    st.warning("🚨 **Manager Approval Required!** A refund request has been flagged by the Billing Guardrail.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Authorize Refund", use_container_width=True):
            st.session_state.awaiting_approval = False
            try:
                with st.spinner("Processing authorization..."):
                    app.update_state(config, {"human_approved": True}, as_node="billing_agent")
                    events = app.stream(None, config, stream_mode="values")
                    for event in events:
                        pass
                
                # Put last message in chat
                snapshot = app.get_state(config)
                state_data = snapshot.values
                if "messages" in state_data and state_data["messages"]:
                    last_msg = state_data["messages"][-1]
                    text = get_clean_string(last_msg)
                    st.session_state.messages.append({"role": "assistant", "content": text})
            except Exception as e:
                st.error(f"Error processing approval: {e}")
                
            st.success("Refund approved and processed!")
            st.rerun()

    with col2:
        if st.button("❌ Reject Request", use_container_width=True):
            st.session_state.awaiting_approval = False
            try:
                with st.spinner("Processing rejection..."):
                    app.update_state(config, {"human_approved": False}, as_node="billing_agent")
                    events = app.stream(None, config, stream_mode="values")
                    for event in events:
                        pass
            except Exception as e:
                pass
                
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Your refund request was reviewed by a support manager and cannot be processed at this time."
            })
            st.rerun()