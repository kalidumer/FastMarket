import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession

# Import database core
from app.core.database import get_session, engine
from app.models.ticket import TicketCreate, Ticket
from app.services.ai_agent import ai_based_ticket

# Router configuration imports
from app.routers.auth_user import router as auth_user_router
from app.routers.ai_support import router as ai_support_router
from app.routers.product import router as product_router
from app.routers.order import router as order_ai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles the automatic database table generation on system start without verbose logs."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        # If the database fails to boot, make it highly visible on the terminal immediately
        print(f"\n🚨 DATABASE CRITICAL CRASH ON LIFESPAN BOOT: {e}\n", file=sys.stderr)
        raise e
    yield

app = FastAPI(title="AI Support Hub Engine", version="1.0.0", lifespan=lifespan)

# =================== MIDDLEWARE FOR FRONTEND CONNECTION ===================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================== INTERCEPTOR FOR CLEAN ERROR DETECTION ===================
@app.middleware("http")
async def absolute_error_cleaner(request: Request, call_next):
    """
    Catches any unhandled router exceptions, isolates the specific file name and 
    line number responsible, and prints a clean, short summary to the terminal.
    """
    try:
        return await call_next(request)
    except Exception as e:
        # 1. Extract raw exception details
        _, _, exc_tb = sys.exc_info()
        
        file_name = "Unknown File"
        line_no = 0
        
        # 2. Walk down the traceback to locate your application code line
        if exc_tb:
            frame = exc_tb.tb_next if exc_tb.tb_next else exc_tb
            file_name = frame.tb_frame.f_code.co_filename
            line_no = frame.tb_lineno
            
        # 3. Print a highly visible, micro-focused debug box to the terminal screen
        print("\n" + "🛑" * 30)
        print(f"💥 ERROR ENCOUNTERED DURING: {request.method} {request.url.path}")
        print(f"📁 LOCATION: {file_name} (Line {line_no})")
        print(f"🏷️  EXCEPTION: {type(e).__name__}")
        print(f"📝 DETAIL: {str(e)}")
        print("🛑" * 30 + "\n")
        
        # 4. Bubble a clean, readable JSON payload back to the client interface
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: [{type(e).__name__}] {str(e)}"}
        )

# ==================== APIS ENDPOINTS MOUNTING ====================
app.include_router(auth_user_router)
app.include_router(ai_support_router)
app.include_router(product_router)
app.include_router(order_ai_router)