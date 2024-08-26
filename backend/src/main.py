from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer 

from src.reports import router as reports
from src.users import router as users

load_dotenv()

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v0/users/token")


app.include_router(reports.router)
app.include_router(users.router)


@app.get("/api/v0")
async def root():
    return {"message": "this is pin-drop"}
