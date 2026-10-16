"""Request bodies for the API."""
from pydantic import BaseModel


class RunRequest(BaseModel):
    case_id: str
    brain: str = "auto"          # rules | llm | auto
    auto_approve: bool = False


class ApprovalRequest(BaseModel):
    approve: bool
