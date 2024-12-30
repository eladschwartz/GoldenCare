from datetime import datetime, timedelta
from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy import func
from .. import models, oauth2
from sqlalchemy.orm import Session
from ..database import get_db

from fastapi.templating import Jinja2Templates
from typing import Optional


templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/goldencare",
     tags = ['GoldenCare']
)

@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html",{"request": request})

@router.get("/", name="home", response_class=HTMLResponse)
def get_treatments(request: Request, selected_date: Optional[datetime] = datetime.now(),current_user : int = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    today = selected_date
    treatments = db.query(models.Treatment).filter(func.date(models.Treatment.timestamp) == func.date(today)).order_by("timestamp").all()
    all_therapist = db.query(models.User).order_by('name').all()
    sorted_time_slots = {}
    new_time_slots = {}
    
    for time in getTimeSlots(db=db):
         new_time_slots.setdefault(time, [])
    
    for treatment in treatments: 
         time = f"{treatment.timestamp.hour:02}:{treatment.timestamp.minute:02}"
         new_time_slots.setdefault(time, [])
         new_time_slots[time].append(treatment)
         sorted_time_slots = dict(sorted(new_time_slots.items()))
    
    return templates.TemplateResponse(
        "dashboard/dashboard.html",
         {"request": request,
          "selected_date": selected_date,
          "time_slots": sorted_time_slots,
          "all_therapist" :all_therapist})
    
    
def getTimeSlots(db: Session = Depends(get_db)):
    result = db.query(
        func.min(models.Treatment.timestamp).label('earliest'),
        func.max(models.Treatment.timestamp).label('latest')
    ).first()
       
    # Default times
    earliest_time = "8:00"
    latest_time = "18:00"
    if result.earliest is not None and result.latest is not None:
        latest_time = f"{result.latest.hour:02}:{result.latest.minute:02}"

    start_time = datetime.strptime(earliest_time, '%H:%M')
    end_time = datetime.strptime(latest_time, '%H:%M')
    time_slots = []
    current_time = start_time
    while current_time <= end_time:
        time_slots.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=15)
    
    return time_slots