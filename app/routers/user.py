from typing import List
from fastapi import HTTPException, status, Depends, APIRouter, Response, Request
from .. import models, schemas, oauth2, utils
from ..database import get_db
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/users",
     tags = ['Users'],
     dependencies=[Depends(oauth2.get_current_user)],
)

# Create user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    
    #hash password
    hashed_passwrod = utils.hash(user.password)
    user.password = hashed_passwrod
    
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
     
    return new_user


@router.put("/password")
async def update_user(passwordUpdate: schemas.PasswordUpdate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_admin)):
    query = select(models.User).where(models.User.id == passwordUpdate.user_id)
    user = (await db.execute(query)).scalar_one_or_none()
    
    try:
        user.password = utils.hash(passwordUpdate.new_password)
        await db.commit()
        await db.refresh(user)
        return Response(status_code=204)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password")
        

# Get specific user
@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
   query = select(models.User).where(models.User.id == id)
   user = (await db.execute(query)).scalar_one_or_none()
    
   if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} doesn not exist")
    
   return user


# Get all treatment of a user
@router.get("/{id}/treatments")
async def get_user_treatments(id: int, db: AsyncSession = Depends(get_db)):
      query = select(models.Treatment).where(models.Treatment.therapist_id == id).order_by(models.Treatment.therapist.desc())
      treatments = (await db.execute(query)).scalars().all()

      if not treatments:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No treatments for user with id: {id}")
    
      return treatments
 
 
# Get all users
@router.get("/", name="users", response_model=List[schemas.UserOut])
async def get_users(request: Request, db: AsyncSession = Depends(get_db)):
     query = (
         select(models.User).order_by(models.User.name)
         .options(joinedload(models.User.department))
         .order_by(models.User.name)
         )
     result = await db.execute(query)
     users = result.scalars().all()
    
     return templates.TemplateResponse(
        "dashboard/therapists.html",
         {"request": request,
          "therapists_data": users})
     
     
# Delete user
@router.delete("/{id}", name="delete_user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: AsyncSession = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    query = select(models.User).where(models.User.id == id)
    user = (await db.execute(query)).scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id:{id} doesn't exist")
    
    try:
         await db.delete(user)
         await db.commit()
    except Exception as e:
        print(e)
        
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
