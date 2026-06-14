from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import test_connection, create_tables
from app.api.api_v1.api import api_router

# Import ALL models here so they register on Base.metadata before create_tables() runs
import app.models  # noqa: F401 — triggers __init__.py which imports all models

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    """
    # Startup
    logger.info("Starting SyncSphere backend application...")
    
    # Test database connection
    if test_connection():
        logger.info("Database connection successful")
        
        # Database Diagnostics
        try:
            from sqlalchemy import text
            from app.db.session import engine
            with engine.connect() as conn:
                db_name = conn.execute(text("SELECT current_database();")).scalar()
                db_user = conn.execute(text("SELECT current_user;")).scalar()
                db_host = conn.execute(text("SELECT inet_server_addr();")).scalar()
                db_version = conn.execute(text("SELECT version();")).scalar()
                logger.info(f"\n==================================================\n📊 RUNTIME DATABASE DIAGNOSTICS:\n- Name: {db_name}\n- User: {db_user}\n- Host Address: {db_host}\n- Version: {db_version}\n==================================================")
        except Exception as diag_err:
            logger.warning(f"Could not run database diagnostics: {diag_err}")
        
        # Run auto-migrations on startup (works on Dev and Render Production)
        try:
            from sqlalchemy import text
            from app.db.session import engine
            with engine.connect() as conn:
                # 1. Add 'INTERN' role to database enum if Postgres
                try:
                    conn.execute(text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'INTERN';"))
                    conn.commit()
                    logger.info("Checked/Added 'INTERN' value to userrole ENUM")
                except Exception as enum_err:
                    logger.debug(f"Skipping ENUM migration: {enum_err}")

                # 2. Add missing columns and alter phone type in users table
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp VARCHAR(10);"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_expires_at TIMESTAMP WITH TIME ZONE;"))
                    conn.execute(text("ALTER TABLE users ALTER COLUMN phone TYPE BIGINT USING phone::bigint;"))
                    conn.commit()
                    logger.info("Successfully checked/added 'otp' and 'otp_expires_at' columns and casted 'phone' to BIGINT")
                except Exception as table_err:
                    logger.warning(f"Could not perform users table auto-migrations: {table_err}")
        except Exception as conn_err:
            logger.warning(f"Auto-migration connection failed: {conn_err}")
            
        # Create tables (in development only)
        if settings.ENVIRONMENT == "development":
            create_tables()
            logger.info("Database tables created")
            
            # Auto-create default admin user for development/testing convenience
            try:
                from app.db.session import SessionLocal
                from app.models.user import User, UserRole, UserStatus
                from app.core.security import get_password_hash
                
                db = SessionLocal()
                try:
                    existing_admin = db.query(User).filter(User.email == "admin@syncsphere.com").first()
                    if not existing_admin:
                        admin_user = User(
                            first_name="System",
                            last_name="Administrator",
                            email="admin@syncsphere.com",
                            phone=1234567890,
                            password_hash=get_password_hash("admin123"),
                            role=UserRole.ADMIN,
                            status=UserStatus.ACTIVE,
                            is_email_verified=True,
                            is_phone_verified=True,
                            department="IT",
                            job_title="System Administrator"
                        )
                        db.add(admin_user)
                        db.commit()
                        logger.info("Default admin user (admin@syncsphere.com / admin123) successfully bootstrapped.")
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"Could not bootstrap default admin user: {e}")
    else:
        logger.error("Failed to connect to database")
        raise Exception("Database connection failed")
    
    logger.info(f"Application started successfully in {settings.ENVIRONMENT} mode")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SyncSphere backend application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A production-ready backend for SyncSphere with FastAPI, PostgreSQL, and SQLAlchemy",
    openapi_url=f"/api/v1/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add TrustedHost middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if test_connection() else "disconnected"
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production"
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
