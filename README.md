# 🧠 Agentic AI System

Evolving **Agentic AI** project developed during the **DEPI Generative AI R4** program.

## Features
- Decision Engine (Functional API)
- Self-correction / Reflection mechanism  
- Tool integration
- Planned FastAPI deployment

## Project Structure

```bash
agentic/
├── core/functional_api/      # Core decision engine logic
├── self_correction/          # Self-correction and validation
├── notebooks/archive/        # Old experiment notebooks
├── app/                      # FastAPI app (future)
├── tools/
├── memory/
├── .env.example
├── requirements.txt
└── corrector.py
```

## Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Add your real keys to .env file

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage
Run the self-correction validator (example):

```bash
python self_correction/corrector.py

Made as part of DEPI GenAI R4.
