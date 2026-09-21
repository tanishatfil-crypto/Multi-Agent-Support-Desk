# ⚡ Multi-Agent Customer Support Desk with LangGraph & HITL

A production-grade, multi-agent customer support system built with **LangGraph**, **Google Gemini**, **Langfuse**, and **Streamlit**. It features automated intent routing, specialized domain sub-agents, Human-in-the-Loop (HITL) billing guardrails, and full observability tracing.

---

## 🏗️ Architecture Flow
[User Input via Streamlit UI]
             │
             ▼
[LangGraph Orchestration State Manager]
             │
             ▼
[Router Agent (Intent Classification)]
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
[Tech]   [General]  [Billing Agent]
Agent    Agent           │
    │        │           ▼
    │        │    (HITL Guardrail Check)
    │        │           │
    │        │    [Interrupted for Manager Approval]
    │        │           │
    │        │     (If Approved by Human)
    │        │           │
    └────────┼───────────┘
             │
             ▼
[Observability & Logging (Langfuse Traces)]
             │
             ▼
[Response Rendered back to Streamlit UI]

---

## 🚀 Key Features

- **Intelligent Intent Routing:** Automatically classifies incoming user messages and directs them to the correct agent node (Billing, Tech, or General).
- **Human-in-the-Loop (HITL) Governance:** High-risk workflows (such as customer refund requests) pause execution state to request manual manager authorization via the Streamlit interface before proceeding.
- **Enterprise Observability:** Integrated with **Langfuse** for complete telemetry, tracing, and debugging across all agent interactions.
- **Resilient Fallback Handling:** Configured with Google Gemini (`gemini-3.5-flash`) to ensure optimal quota management and low-latency performance.
- **Polished SaaS UI:** Built with custom dark-mode CSS, session management, and clean markdown rendering.

---

## 🛠️ Tech Stack

- **Orchestration:** LangGraph / LangChain
- **LLM:** Google Gemini (`gemini-3.5-flash`)
- **Observability:** Langfuse
- **Frontend UI:** Streamlit

---

## ⚙️ Local Installation & Setup

Follow these steps to run the application locally on your machine:

### 1. Clone the Repository
```bash
git clone [https://github.com/tanishatfil-crypto/Multi-Agent-Support-Desk.git](https://github.com/tanishatfil-crypto/Multi-Agent-Support-Desk.git)
cd Multi-Agent-Support-Desk

### 2. Create a Virtual Environment (Recommended)

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory and add your API keys:

Code snippet
GOOGLE_API_KEY=your_gemini_api_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=[https://cloud.langfuse.com](https://cloud.langfuse.com)
5. Run the Application
Bash
streamlit run app.py
Open your browser at http://localhost:8502 to interact with the support desk!

💡 Example Queries to Test
Billing Path (Triggers HITL Guardrail): "I was charged twice on my last invoice. Refund me!"

Tech Support Path: "My app keeps crashing whenever I try to upload a PDF file."

General Support Path: "What are your support team's operating hours?