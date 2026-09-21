import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import SupportState

load_dotenv()

# Set model to required gemini-3.6-flash
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2
)

def extract_text(response):
    if hasattr(response, "content"):
        content = response.content
    else:
        content = response

    if isinstance(content, list) and len(content) > 0:
        first = content[0]
        if isinstance(first, dict):
            return first.get("text", str(first))
        return str(first)
    elif isinstance(content, dict):
        return content.get("text", str(content))
    
    return str(content)

def router_node(state: SupportState):
    user_msg = state["messages"][-1]["content"] if isinstance(state["messages"][-1], dict) else state["messages"][-1].content
    
    prompt = f"""You are an intelligent triage agent. Classify the following customer query into exactly one of three categories: 'billing', 'tech', or 'general'.
    
    Query: "{user_msg}"
    
    Respond ONLY with the category name in lowercase. Do not add any punctuation or extra text."""
    
    response = llm.invoke(prompt)
    category = extract_text(response).strip().lower()
    
    return {
        "category": category,
        "requires_human_approval": (category == "billing")
    }

def billing_agent_node(state: SupportState):
    user_msg = state["messages"][-1]["content"] if isinstance(state["messages"][-1], dict) else state["messages"][-1].content
    
    prompt = f"You are an empathetic Billing Support Agent. Handle this billing issue professionally:\nQuery: {user_msg}"
    response = llm.invoke(prompt)
    clean_text = extract_text(response)
        
    return {
        "messages": state["messages"] + [{"role": "assistant", "content": clean_text}],
        "resolution": "Processed by Billing Agent (Approved)"
    }

def tech_agent_node(state: SupportState):
    user_msg = state["messages"][-1]["content"] if isinstance(state["messages"][-1], dict) else state["messages"][-1].content
    
    prompt = f"You are a Technical Support Agent. Provide step-by-step troubleshooting for this issue:\nQuery: {user_msg}"
    response = llm.invoke(prompt)
    clean_text = extract_text(response)

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": clean_text}],
        "resolution": "Resolved by Tech Support Agent"
    }

def general_agent_node(state: SupportState):
    user_msg = state["messages"][-1]["content"] if isinstance(state["messages"][-1], dict) else state["messages"][-1].content
    
    prompt = f"You are a Helpful Support Agent. Answer this inquiry clearly:\nQuery: {user_msg}"
    response = llm.invoke(prompt)
    clean_text = extract_text(response)

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": clean_text}],
        "resolution": "Answered by General Agent"
    }