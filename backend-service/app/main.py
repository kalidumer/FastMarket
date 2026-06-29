import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession

# import from folder

from app.core.database import get_session, engine
from app.models.ticket import TicketCreate, Ticket

from app.services.ai_agent import ai_based_ticket

#for Router

from app.routers.auth_user import router as auth_user_router
from app.routers.ai_support import router as ai_support_router

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

#===================middleware to accept the frontend========

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows easy staging connection for both your apps
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== APIS ENDPOINTS ====================

#================in the future all endpoint will add like this================================
app.include_router(auth_user_router)
app.include_router(ai_support_router)
