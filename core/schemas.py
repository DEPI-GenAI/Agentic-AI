from pydantic import BaseModel
from enum import Enum
from typing import Optional

class Action(str, Enum):
    CREATE_TICKET = "CREATE_TICKET"
    ASK_FOR_MORE_INFO = "ASK_FOR_MORE_INFO"
    REJECT_REQUEST = "REJECT_REQUEST"
    FLAG_OUT_OF_SCOPE = "FLAG_OUT_OF_SCOPE"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"

class DecisionRequest(BaseModel):
    user_request: str
    user_id: Optional[str] = "anonymous"

class DecisionResponse(BaseModel):
    action: str          # Changed to str (more flexible)
    reason: str