from typing import List
from fastapi import HTTPException, status, Depends, APIRouter, Response, Request
from .. import models, schemas, oauth2
from ..database import get_db
from fastapi.templating import Jinja2Templates
from sqlalchemy import exists, and_, or_,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
from datetime import datetime
import pytz

templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/patients",
     tags = ['Patients'],
     dependencies=[Depends(oauth2.get_current_user)],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PatientOut)
async def create_patient(patient: schemas.PatientCreate, db: AsyncSession = Depends(get_db)): 
    new_patient = models.Patient(**patient.model_dump())
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
     
    return new_patient


@router.get("/", name="patients", response_model=List[schemas.PatientOut])
async def get_tempele_patients(request:Request, db: AsyncSession = Depends(get_db)):
    query = select(models.Patient).options(joinedload(models.Patient.department)).order_by(models.Patient.name)
    result = await db.execute(query)
    patients = result.scalars().all()
    
    return templates.TemplateResponse("dashboard/patients.html", {"request": request, "data": patients})


async def get_patients_without_treatments(db, target_date):
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    elif isinstance(target_date, datetime):
        target_date = target_date.date()
    
    treatments_subquery = (
        select(models.Treatment.id)
        .where(
            and_(
                models.Treatment.patient_id == models.Patient.id,
                func.date(models.Treatment.timestamp) == target_date
            )
        )
    )
    
    query = (
        select(models.Patient)
        .where(
            and_(
                ~exists(treatments_subquery),
                or_(
                    models.Patient.release_date.is_(None),
                    models.Patient.release_date > target_date
                )
            )
        )
        .order_by(models.Patient.name)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())
     
     
@router.get("/all", name="patients", response_model=List[schemas.PatientOut])
async def get_all_patients(request:Request, date:str, db: AsyncSession = Depends(get_db)):
    
    return await get_patients_without_treatments(db, date)


@router.get("/{id}", response_model=schemas.PatientOut)
async def get_patient(id: int, db: AsyncSession = Depends(get_db)):
    query = select(models.Patient).where(models.Patient.id == id)
    result = await db.execute(query)
    patient = result.scalar_one_or_none
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient with id: {id} doesn not exist")
    
    return patient


@router.put("/{id}")
async def update_patient(id: int, updated_model: schemas.PatientOut, db: AsyncSession = Depends(get_db)):
    patient = await db.get(models.Patient, id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"patient with id: {id} does not exist"
        )
    
    update_data = updated_model.model_dump(exclude_unset=True)
    query = update(models.Patient).where(models.Patient.id == id).values(**update_data)
    
    await db.execute(query)
    await db.commit()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(id: int, db: AsyncSession = Depends(get_db)):
    query = select(models.Patient).where(models.Patient.id == id)
    patient = (await db.execute(query)).scalar_one_or_none()
    
    
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient with id:{id} doesn't exist")
    
    stmt = delete(models.Patient).where(models.Patient.id == id)
    await db.execute(stmt)
    await db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)