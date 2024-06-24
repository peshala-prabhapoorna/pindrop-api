from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v0/")
async def root():
    return {"message": "returns something"}
