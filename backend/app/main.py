from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Pipe It!! API",
    description="Backend API for Pipe It!! - On-Chain Invoice Factoring with Intelligent Yield and Real-Time Market Insights",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Pipe It!! API",
        "description": "On-Chain Invoice Factoring with Intelligent Yield and Real-Time Market Insights",
        "documentation": "/docs",
    }

# Import routers - make sure these import paths match your actual structure
from app.api.token_routes import router as token_router
from app.api.invoice_routes import router as invoice_router
from app.api.agent_routes import router as agent_router
from app.api.rate_routes import router as rate_router
from app.api.trading_routes import router as trading_router
from app.api.vault_routes import router as vault_router

# Include routers
app.include_router(token_router, prefix="/api")
app.include_router(invoice_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(rate_router, prefix="/api")
app.include_router(trading_router, prefix="/api")
app.include_router(vault_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)