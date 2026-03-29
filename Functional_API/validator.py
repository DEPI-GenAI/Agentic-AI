# validator.py
from schemas import DecisionResponse

def validate_output(data):
    try:
        return DecisionResponse(**data)
    except Exception:
        return None