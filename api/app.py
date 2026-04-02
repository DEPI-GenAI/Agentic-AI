from __future__ import annotations

import asyncio

from fastapi import FastAPI, HTTPException

from core.orchestrator import Orchestrator
from schemas import AgentRequest, AgentResponse, DecisionRequest, DecisionResponse
from core.config import settings


app = FastAPI(
    title="Agentic AI API",
    description="Single orchestrated agent with modular capabilities",
    version="2.0",
)

orchestrator = Orchestrator()


@app.get("/")
async def root():
    return {"message": "✅ Agentic AI API is running. Go to /docs"}


@app.post("/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    try:
        # Offload to a thread since local models can be slow/blocking.
        result = await asyncio.to_thread(orchestrator.handle_request, request.user_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Backward-compatible endpoint (existing tests/clients)
@app.post("/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest):
    try:
        # Keep original behavior: decision-only and with timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(orchestrator.ticket_agent.decide, request.user_request),
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request took too long. Model is slow on CPU.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

