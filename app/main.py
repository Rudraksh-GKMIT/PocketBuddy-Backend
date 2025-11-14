from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes import users
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PocketBuddy API - Role-based System")

app.include_router(users.router)


@app.get("/")
def home():
    return {"message": "Welcome to PocketBuddy API with Roles"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
