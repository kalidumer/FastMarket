from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

# Database Table Layout
class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    feedback_text: str
    
    # AI Enrichment Columns (Pre-configured for Phase 3)
    urgency_level: Optional[str] = Field(default="Processing...")
    customer_sentiment: Optional[str] = Field(default="Processing...")
    suggested_action: Optional[str] = Field(default="Processing...")
    draft_reply: Optional[str] = Field(default="Processing...")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# API Input Validation Schema 
class TicketCreate(BaseModel):
    customer_name: str
    feedback_text: str