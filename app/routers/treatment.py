from typing import List, Optional
from fastapi import HTTPException, status, Depends, APIRouter, Response, Request
from .. import models, schemas, oauth2
from ..database import get_db
from datetime import datetime
from sqlalchemy import func, and_
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/treatments",
     tags = ['Treatments'],
     dependencies=[Depends(oauth2.get_current_user)],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TreatmentOut)
async def create_treatment(treatment: schemas.TreatmentCreate, db: AsyncSession = Depends(get_db)):
    new_treatment = models.Treatment(**treatment.model_dump())
    db.add(new_treatment)
    await db.commit()
    await db.refresh(new_treatment)
     
    return new_treatment


@router.get("/", response_model=List[schemas.TreatmentOut])
async def get_treatments(db: AsyncSession = Depends(get_db)):
  
    query = select(models.Treatment)
    treatments = (await db.execute(query)).scalars().all()
    
    return treatments

@router.get("/{id}", response_model=schemas.TreatmentOut)
async def get_treatment(id: int, db: AsyncSession = Depends(get_db)):
    
    query = select(models.Treatment).where(models.Treatment.id == id)
    treatment = (await db.execute(query)).scalar_one_or_none()
    
    if not treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Treatment with id: {id} doesn not exist")
    
    return treatment

@router.get("/user/{user_id}", response_model=List[schemas.TreatmentOut])
async def get_treatments_for_user(user_id:int, request: Request, selected_date: Optional[datetime] = datetime.now(), db: AsyncSession = Depends(get_db)):
    
    today = selected_date
    query = select(models.User).where(models.User.id == user_id)
    therapist = (await db.execute(query)).scalar_one_or_none()
    
    query = select(models.Treatment).options(joinedload(models.Treatment.patient)).where(
        and_(models.Treatment.therapist_id == user_id,
             func.date(models.Treatment.timestamp) == func.date(today)))
    treatments = (await db.execute(query)).scalars().all()
    
    
    data = {}
    for treatment in treatments:
         time = f"{treatment.timestamp.hour:02}:{treatment.timestamp.minute:02}"
         data[time] = [treatment.id, treatment.patient]
         
         
    data_to_return = {
            "therapist": therapist,
            "treatments": data,
            "selected_date": today,
        }
  
    return templates.TemplateResponse(
        "dashboard/therapist.html",
         {"request": request,
          "data": data_to_return})


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment(id: int, db: AsyncSession = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    query = select(models.Treatment).where(models.Treatment.id == id)
    treatment = (await db.execute(query)).scalar_one_or_none()
    
    if treatment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Treatment with id:{id} doesn't exist")
    
    await db.delete(treatment)
    await db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}",response_model=schemas.TreatmentOut)
async def update_treatment(id: int, updated_treatment: schemas.TreatmentOut, db: AsyncSession = Depends(get_db)):
    query = update(models.Treatment).where(models.Treatment.id == id).values(**updated_treatment)
    treatment = (await db.execute(query)).scalar_one_or_none()
    
    if treatment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"treatment with id: {id} does not exist")
    
    
    await db.commit()
  
    return treatment


@router.post("/copy")
async def copy_treatments_by_date_range(request: schemas.TreatmentCopyRequest, db: AsyncSession = Depends(get_db)):
    
    try:
        query = select(models.Treatment).where(
        and_(models.Treatment.therapist_id == request.therapist_id,
             func.date(models.Treatment.timestamp) == func.date(request.from_date)))
          
        date_diff = request.to_date - request.from_date
        # Get treatments within the date range for the specified therapist
        treatments_to_copy = (await db.execute(query)).scalars().all()
           
        # Create new treatment instances with copied data
        new_treatments = []
        for treatment in treatments_to_copy:
            new_treatment = models.Treatment(
                patient_id=treatment.patient_id,
                therapist_id=treatment.therapist_id,
                timestamp=treatment.timestamp + date_diff,
            )
            new_treatments.append(new_treatment)

        if new_treatments:
            db.bulk_save_objects(new_treatments)
            db.commit()
            

    except Exception as e:
        db.rollback()
        raise Exception(f"Error copying treatments: {str(e)}")



