
from fastapi import FastAPI
# import app.model.users as users
from app.db.database import engine , SessionLocal
from app.db.database import Base
from app.routes import users,admin,transaction

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PocketBuddy API - Role-based System")

app.include_router(users.router)


@app.get("/")
def home():
    return {"message": "Welcome to PocketBuddy API with Roles"}

if __name__ == "__main__":
    main()
