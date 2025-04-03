from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Factora+ API",
    description="Backend API for Factora+ - On-Chain Invoice Factoring Platform",
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
    return {"message": "Welcome to Factora+ API"}

# Import and include API routers here
# from app.api.routes import router
# app.include_router(router)

# At the bottom of the imports
from app.api.test_routes import router as test_router
from app.api.token_routes import router as token_router

# After the app initialization
app.include_router(test_router)
app.include_router(token_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)