# 🧠 Agentic AI System

Evolving **Agentic AI** project built during the **DEPI Generative AI R4** program.

## Features
- Decision Engine using Functional API
- Self-correction / Reflection mechanism
- Tool calling & validation
- Planned FastAPI deployment

## Folder Structure

```bash
agentic/
├── core/functional_api/      # Decision engine + core logic
├── self_correction/          # Self-correction module (`corrector.py`)
├── notebooks/archive/        # Old experiment notebooks
├── app/                      # Future FastAPI app
├── tools/
├── memory/
├── requirements.txt
├── .env.example
└── .gitignore
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
```

Made as part of DEPI GenAI R4.
