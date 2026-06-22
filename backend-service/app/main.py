import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession

# 🟢 FIXED IMPORTS: Explicitly routing to our new core and models folders
from app.core.database import get_session, engine
from app.models.ticket import TicketCreate, Ticket

# 🟢 FIXED IMPORT: Mapping accurately to your AI worker path
from app.services.ai_agent import ai_based_ticket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API_BOOT")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles the automatic database table generation on system start."""
    logger.info("Connecting to Supabase cloud network...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database structural validation complete. Tables are live!")
    except Exception as e:
        logger.critical(f"Database boot sync failed: {e}")
        raise e
    yield

app = FastAPI(title="AI Support Hub Engine", version="1.0.0", lifespan=lifespan)

#======================middleware to accept the frontend==

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows easy staging connection for both your apps
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== APIS ENDPOINTS ====================

# Note: Changed pathing slightly to match your explicit design
@app.post("/api/create_ticket", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    background_tasks: BackgroundTasks, 
    session: AsyncSession = Depends(get_session)
):
    try:
        new_ticket = Ticket(
            customer_name=payload.customer_name,
            feedback_text=payload.feedback_text
        )
        session.add(new_ticket)
        await session.commit()
        await session.refresh(new_ticket)
        
        # Assign the slow AI processing call directly to our background worker pool
        background_tasks.add_task(
            ai_based_ticket,
            tiket_id=new_ticket.id,
            feedback_text=new_ticket.feedback_text
        )

        return {
            "status": "success",
            "message": "the new ticket is added to the supabase successfully!",
            "Ticket ID": new_ticket.id,
        }
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket: {str(exc)}",
        ) from exc


@app.get("/api/get_tickets")
async def get_all_tickets(session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Ticket).order_by(Ticket.created_at.desc())
        result = await session.execute(statement)
        tickets = result.scalars().all()
        return {"total_count": len(tickets), "tickets": tickets}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tickets: {str(exc)}",
        ) from exc