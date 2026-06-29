import logging
from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_session
from app.models.ticket import TicketCreate, Ticket
from app.services.ai_agent import ai_based_ticket

# Auth guards and user model tracking
from app.core.auth_guard import get_current_user, RoleChecker
from app.models.user import User, UserRole

logger = logging.getLogger("AI_SUPPORT_ROLES")

router = APIRouter(prefix="/api", tags=["AI Ticket Support Module"])

SUPPORT_QUALIFIED_ROLES = RoleChecker([UserRole.SUPPORT_AGENT, UserRole.MANAGER, UserRole.ADMIN])


# ==================== APIS ENDPOINTS ====================

@router.post("/create_ticket", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    background_tasks: BackgroundTasks, 
    session: AsyncSession = Depends(get_session)
):
    """Public endpoint for customers to submit tickets. Offloads AI analysis to background workers."""
    try:
        new_ticket = Ticket(
            customer_name=payload.customer_name,
            feedback_text=payload.feedback_text
        )
        session.add(new_ticket)
        await session.commit()
        await session.refresh(new_ticket)
        
        # Assign the background worker task to process the AI analysis asynchronously
        background_tasks.add_task(
            ai_based_ticket,
            tiket_id=new_ticket.id,
            feedback_text=new_ticket.feedback_text
        )

        return {
            "status": "success",
            "message": "The new ticket was added to Supabase successfully!",
            "Ticket ID": new_ticket.id,
        }
        
    except Exception as exc:
        await session.rollback()
        logger.error(f"Error creating ticket: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket: {str(exc)}",
        ) from exc


@router.get("/get_tickets")
async def get_all_tickets(
    session: AsyncSession = Depends(get_session),
    current_agent: User = Depends(SUPPORT_QUALIFIED_ROLES)):
    """Protected endpoint for support agents to read all submitted tickets."""
    try:
        statement = select(Ticket).order_by(Ticket.created_at.desc())
        result = await session.execute(statement)
        tickets = result.scalars().all()
        
        return {
            "total_count": len(tickets), 
            "accessed_by": current_agent.email,
            "tickets": tickets
        }
    except Exception as exc:
        logger.error(f"Error reading tickets: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tickets: {str(exc)}",
        ) from exc