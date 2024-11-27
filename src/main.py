from dotenv import load_dotenv
from fastapi import FastAPI

from src.reports import router as reports
from src.users import router as users


load_dotenv()

app = FastAPI(
    title="pindrop-api",
    description="API for location based issue reporting.",
    version="1.0.0",
    contact={
        "name": "RAP Prabhapoorna",
        "url": "https://www.linkedin.com/in/peshala-prabhapoorna/",
        "email": "peshalaprabhapoorna@gmail.com",
    },
    license_info={
        "name": "AGPL-3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0",
    }
)


app.include_router(reports.router)
app.include_router(users.router)


@app.get("/api/v0")
async def root():
    return {"message": "this is pin-drop"}
