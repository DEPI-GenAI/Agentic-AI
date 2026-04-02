# 🧠 Agentic AI System
An autonomous AI agent designed for legal contract decision-making and secure data analytics, built during the DEPI Generative AI R4 program.

## 🚀 Advanced Features
Intelligent Routing: Uses an LLM-based Router to accurately distinguish between data analytics requests and legal contract disputes.

Self-Correction (Reflection): Features an iterative repair loop that captures code execution errors and sends them back to the LLM for autonomous fixing.

Semantic Schema Mapping: Robustly handles user synonyms (e.g., "dept" → "department") and resolves column ambiguity before code generation.

Double-Check Validation: Integrates a strict logic-gate using Groq (Llama-3) to verify that generated code is logically correct before execution.

Secure AST Sandbox: A hardened Python execution environment that prevents unauthorized raw data access and limits operations to approved analytics functions.

## 📂 Project Structure

```bash
Agentic-AI/
├── agents/             # Modular Agents (Router, Analytics, Ticket)
├── api/                # FastAPI implementation and endpoints
├── core/               # Orchestrator and core system logic
├── extracted/          # Validated logic migrated from experimental notebooks
├── guards/             # Security guards (AST Sandbox, Policy guards)
├── models/             # LLM adapters (Phi-3.5, Groq Validator)
├── memory/             # Local data storage (CSVs)
├── tests/              # API and logic test suites
├── requirements.txt    # System dependencies
├── .env.example        # Environment template (API keys)
└── .gitignore          # Git exclusion rules
```

## 🛠️ Setup
1. Configure Environment:
```bash
cp .env.example .env
# Add your GROQ_API_KEY and HUGGINGFACE_TOKEN to .env
```

2. Install Dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
uvicorn core.api.app:app --reload
```

## 🚦 Usage
Send a POST request to the orchestrated agent endpoint:

```bash
# Example Data Analytics Query
curl -X POST "http://127.0.0.1:8000/agent" \
     -H "Content-Type: application/json" \
     -d '{"user_request": "What is the average salary per department?"}'
```
Made as part of DEPI GenAI R4.
