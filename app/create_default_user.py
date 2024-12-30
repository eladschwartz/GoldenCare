from app.models import User
from app.database import get_db
from app.utils import hash
from app.config import settings


def create_default_user():
    db = next(get_db())
    
    try:
        admin_user = db.query(User).filter(
            User.email == settings.admin_email
            ).first()
        if not admin_user:
            admin_user = User(
                name=settings.admin_name,
                department_id = 1,
                email=settings.admin_email,
                hashed_password=hash(settings.admin_password),
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created successfully!")
        else:
            print("Admin user already exists!")
    finally:
        db.close()
 
        

if __name__ == "__main__":
  create_default_user()