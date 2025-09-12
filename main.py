from fastapi import FastAPI

app = FastAPI(
    title="Konnect API", description="Campus Tools with SolanaPay", version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Hello from Konnect API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "konnect-backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
