from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Smart Document Bot API",
    description="AI-powered document processing and analysis system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Smart Document Bot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Smart Document Bot API"}

@app.get("/api/v1/status")
async def api_status():
    return {
        "status": "operational",
        "version": "1.0.0",
        "service": "Smart Document Bot API",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/status",
            "/docs"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
