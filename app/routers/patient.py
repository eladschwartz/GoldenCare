from typing import List
from fastapi import HTTPException, status, Depends, APIRouter, Response, Request
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.templating import Jinja2Templates
from sqlalchemy import not_, exists, and_, func
from datetime import datetime

templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/patients",
     tags = ['Patients'],
     dependencies=[Depends(oauth2.get_current_user)],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)): 
    new_patient = models.Patient(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
     
    return new_patient


@router.get("/", name="patients", response_model=List[schemas.PatientOut])
def get_tempele_patients(request:Request, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).order_by("name").all()
    
    return templates.TemplateResponse("dashboard/patients.html", {"request": request, "data": patients})


def get_patients_without_treatments(db, target_date):
    if isinstance(target_date, str):
        target_date = datetime.fromisoformat(target_date)
        
    #Get all patients that don't have treamtent on a spcefic date and also their release date > today
    return (
        db.query(models.Patient)
        .filter(
            and_(
                not_(exists().where(
                    and_(
                        models.Treatment.patient_id == models.Patient.id,
                        func.date(models.Treatment.timestamp) == target_date
                    ))
                ),
                (models.Patient.release_date.is_(None) | (models.Patient.release_date > target_date))
            )
        )
        .order_by("name")
        .all()
    )
    
    
@router.get("/all", name="patients", response_model=List[schemas.PatientOut])
def get_all_patients(request:Request, date:str, db: Session = Depends(get_db)):
    
    return get_patients_without_treatments(db, date)



@router.get("/{id}", response_model=schemas.PatientOut)
def get_patient(id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient with id: {id} doesn not exist")
    
    return patient


@router.put("/{id}", response_model=schemas.PatientOut)
def update_patient(id: int, updated_model: schemas.PatientOut, db: Session = Depends(get_db)):
    patient_query = db.query(models.Patient).filter(models.Patient.id == id)
    patient = patient_query.first()
    
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"patient with id: {id} does not exist")
    
    patient_query.update(updated_model.model_dump(),synchronize_session=False)
    db.commit()
  
    return patient_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(id: int, db: Session = Depends(get_db)):
    patient_query = db.query(models.Patient).filter(models.Patient.id == id)
    
    patient = patient_query.first()
    
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient with id:{id} doesn't exist")
    
    #Check if role is admin
    
    patient_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

