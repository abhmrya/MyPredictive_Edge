from fastapi import FastAPI

app = FastAPI(
    title="PredictiveEdge API",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "PredictiveEdge API is running"
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok"
    }