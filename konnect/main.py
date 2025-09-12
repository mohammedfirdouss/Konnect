"""FastAPI main application module"""

from fastapi import FastAPI

app = FastAPI(
    title="Konnect",
    description="Campus Tools with SolanaPay",
    version="0.1.0"
)


@app.get("/")
async def read_root():
    """Hello World endpoint"""
    return {"message": "Hello World", "app": "Konnect"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}