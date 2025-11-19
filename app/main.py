from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes import users, transaction, admin, summary
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="PocketBuddy API - Role-based System")

origins = [
    "http://127.0.0.1:5500",  # Your frontend
    "http://localhost:5500",  # Alternative
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(transaction.router)
app.include_router(summary.router)


@app.get("/")
def home():
    return {"message": "Welcome to PocketBuddy API with Roles"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
