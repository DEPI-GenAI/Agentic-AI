from fastapi import FastAPI, HTTPException
from schemas import DecisionRequest, DecisionResponse
from decision_engine import fullsystem
import asyncio

app = FastAPI(
    title="Decision Engine API",
    description="AI-powered decision making assistant",
    version="1.0"
)

@app.get("/")
async def root():
    return {"message": "✅ Decision Engine API is running. Go to /docs"}

@app.post("/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest):
    try:
        # Add timeout because model is slow on CPU
        result = await asyncio.wait_for(
            asyncio.to_thread(fullsystem, request.user_request),
            timeout=90.0   # 90 seconds max
        )
        
        if not isinstance(result, dict) or "action" not in result:
            raise HTTPException(status_code=500, detail="Invalid model output")

        return {
            "action": result.get("action", "FLAG_OUT_OF_SCOPE"),
            "reason": result.get("reason", "No reason provided by the model.")
        }
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request took too long. Model is slow on CPU.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")