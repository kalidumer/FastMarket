import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

# Read from your local .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# --- RESILIENT FALLBACK CONNECTION STRING ---
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres.yokbsgdcuymjirrsruvv:Frealem%2A123@aws-0-us-east-1.pooler.supabase.com:6543/postgres?superseded=false"

# Build the asynchronous database driver engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,                 # Prints raw SQL requests into your terminal for tracking
    pool_pre_ping=True,        # Validates line health before executing queries
    connect_args={
        "timeout": 30,
        "command_timeout": 30,
        "statement_cache_size": 0,  # Required for Supabase poolers that do not support prepared statements well
    }
)

# Set up the short-lived query session builder
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

# FastAPI dependency injector to feed routes safe database connection instances
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session