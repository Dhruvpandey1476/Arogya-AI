from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
