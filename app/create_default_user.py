from app.models import User 
from .database import get_db
from .utils import hash
from .config import settings

def create_default_user():
    db = get_db()
    admin_user = db.query(User).filter(
            User.email == settings.admin_email
        ).first()
    if not admin_user:
            # Create new admin user
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
 
        

if __name__ == "__main__":
  create_default_user()