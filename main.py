"""
FastAPI main application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from app.routes.chat import router as chat_router

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Fraud Detection Chatbot",
    description="A defensive security chatbot to help users identify potentially fraudulent transactions",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(chat_router)


@app.get("/")
async def serve_index():
    """
    Serve the main HTML page.
    
    Returns:
        FileResponse: HTML file response.
    """
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status.
    """
    return {"status": "healthy", "service": "fraud-detection-chatbot"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=debug
    )