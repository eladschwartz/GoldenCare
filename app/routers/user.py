from typing import List
from fastapi import HTTPException, status, Depends, APIRouter, Response, Request
from .. import models, schemas, oauth2, utils
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/users",
     tags = ['Users'],
     dependencies=[Depends(oauth2.get_current_user)],
)

# Create user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    #hash password
    hashed_passwrod = utils.hash(user.password)
    user.password = hashed_passwrod
    
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
     
    return new_user



@router.put("/password")
def update_user(passwordUpdate: schemas.PasswordUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_admin)):
    user = db.query(models.User).filter(models.User.id == passwordUpdate.user_id).first()
    try:
        user.password = utils.hash(passwordUpdate.new_password)
        db.commit()
        db.refresh(user)
        return Response(status_code=204)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password")
        

# Get specific user
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} doesn not exist")
    
    return user


# Get all treatment of a user
@router.get("/{id}/treatments")
def get_user_treatments(id: int, db: Session = Depends(get_db)):
     treatments = db.query(models.Treatment)\
        .filter(models.Treatment.therapist_id == id)\
        .order_by(models.Treatment.timestamp.desc())\
        .all()

     if not treatments:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No treatments for user with id: {id}")
    
     return treatments
 
 
# Get all users
@router.get("/", name="users", response_model=List[schemas.UserOut])
def get_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).order_by("name").all()
    
    
    return templates.TemplateResponse(
        "dashboard/therapists.html",
         {"request": request,
          "therapists_data": users})
    


# Delete user
@router.delete("/{id}", name="delete_user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    
    user = user_query.first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id:{id} doesn't exist")
    
 
    try:
        user_query.delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        print(e)
        
  
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
