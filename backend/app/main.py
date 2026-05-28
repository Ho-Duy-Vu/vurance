from fastapi import FastAPI

app = FastAPI(
    title="ClaimFlow API",
    version="1.0.0",
    description="AI-powered insurance claims processing platform",
)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
