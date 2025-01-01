from datetime import datetime, timedelta
from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from .. import models, oauth2
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.templating import Jinja2Templates
from typing import Optional
from sqlalchemy.orm import joinedload



templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/goldencare",
     tags = ['GoldenCare']
)

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html",{"request": request})

@router.get("/", name="home", response_class=HTMLResponse)
async def get_treatments(request: Request, selected_date: Optional[datetime] = datetime.now(),current_user : int = Depends(oauth2.get_current_user), db: AsyncSession = Depends(get_db)):
    today = selected_date
    query = select(models.Treatment).options(joinedload(models.Treatment.patient)).where(func.date(models.Treatment.timestamp) == func.date(today)).order_by(models.Treatment.timestamp)
    
    treatments_results = await db.execute(query)
    treatments = treatments_results.scalars().all()

    query_therapist = select(models.User).order_by(models.User.name)
    results_therapist = await db.execute(query_therapist)
    therapists = results_therapist.scalars().all()
    
    sorted_time_slots = {}
    new_time_slots = {}
    
    for time in await getTimeSlots(db=db):
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
          "all_therapist" :therapists})
    
    
async def getTimeSlots(db: AsyncSession = Depends(get_db)):
    query = select(
    func.min(models.Treatment.timestamp).label('earliest'),
    func.max(models.Treatment.timestamp).label('latest')
)
    result_times = await db.execute(query)
    result = result_times.one_or_none() 
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