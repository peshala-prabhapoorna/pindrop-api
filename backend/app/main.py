from fastapi import FastAPI

from app.routers import reports

app = FastAPI()


app.include_router(reports.router)


@app.get("/api/v0")
async def root():
    return {"message": "this is pin-drop"}
