import os
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler
from src.graph import build_support_graph

load_dotenv()

langfuse_handler = CallbackHandler()

def run_test():
    app = build_support_graph()
    
    # Thread ID se state memory link hoti hai
    config = {
        "configurable": {"thread_id": "session_customer_101"},
        "callbacks": [langfuse_handler]
    }
    
    user_query = "I was charged twice, I need a refund immediately!"
    
    initial_state = {
        "messages": [{"role": "user", "content": user_query}],
        "category": "",
        "requires_human_approval": False,
        "resolution": ""
    }

    print(f"\n📩 User Query: '{user_query}'")
    print("--------------------------------------------------")
    
    # First Execution (Graph billing agent se pehle Pause ho jayega interrupt ki wajah se)
    events = app.stream(initial_state, config, stream_mode="values")
    for event in events:
        if "category" in event and event["category"]:
            print(f"🏷️  Detected Category: {event['category']}")

    # State check karo ki interrupt kahan hua
    snapshot = app.get_state(config)
    
    if snapshot.next and "billing_agent" in snapshot.next:
        print("\n🛑 [HUMAN-IN-THE-LOOP INTERRUPT]")
        print("Refund request flagged! Manager approval required before proceeding.")
        
        # Human decision simulate kar rahe hain
        human_approval = "YES" # Change to "NO" to test rejection logic
        print(f"👤 Manager Decision: Approved ({human_approval})")
        print("--------------------------------------------------")
        
        # Resume execution with human decision
        for event in app.stream(None, config, stream_mode="values"):
            if "resolution" in event and event["resolution"]:
                print(f"📝 Status/Resolution     : {event['resolution']}")
                print(f"🛑 Requires Human Approval: {event['requires_human_approval']}")
                final_msg = event["messages"][-1]
                response_text = final_msg.get("content", final_msg) if isinstance(final_msg, dict) else final_msg.content
                print(f"🤖 Final Agent Response   :\n{response_text}")

if __name__ == "__main__":
    run_test()