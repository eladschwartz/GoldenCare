from app.models import User
from app.database import get_db
from app.utils import hash
from app.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def create_default_user():
    db : AsyncSession = next(get_db())
    
    try:
        query = select(User).where(User.email == settings.admin_email)
        admin_user = (await db.execute(query)).scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                name=settings.admin_name,
                department_id = 1,
                email=settings.admin_email,
                password=hash(settings.admin_password),
            )
            db.add(admin_user)
            await db.commit()
            print("Default admin user created successfully!")
        else:
            print("Admin user already exists!")
    finally:
        db.close()
 
        

if __name__ == "__main__":
  create_default_user()