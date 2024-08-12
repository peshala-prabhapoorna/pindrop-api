from fastapi import FastAPI

from src.reports import router as reports

app = FastAPI()


app.include_router(reports.router)


@app.get("/api/v0")
async def root():
    return {"message": "this is pin-drop"}
