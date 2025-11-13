from sqlalchemy.orm import Session
from app.model import users

from app.constants import ADMIN, MEMBER

def seed_roles(db: Session):
    existing_roles = db.query(users.Role).all()
    if not existing_roles:
        admin_role = users.Role(name=ADMIN)
        user_role = users.Role(name=MEMBER)
        db.add_all([admin_role, user_role]) 
        db.commit()
        print("Roles seeded successfully.")
