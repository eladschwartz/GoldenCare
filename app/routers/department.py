
from typing import List
from fastapi import HTTPException, status, Depends, APIRouter, Response, Request
from .. import models, schemas, oauth2
from ..database import get_db
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/departments",
     tags = ['Departments'],
     dependencies=[Depends(oauth2.get_current_user)],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.DepartmentOut)
async def create_department(department: schemas.DepartmentCreate, db: AsyncSession = Depends(get_db)):
    
    new_department = models.Department(**department.model_dump())
    db.add(new_department)
    await db.commit()
    await db.refresh(new_department)
     
    return new_department


async def get_all_departments(db: AsyncSession):
    query = select(models.Department)
    departments = (await db.execute(query)).scalars().all()

    return departments


@router.get("/all", response_model=List[schemas.DepartmentOut])
async def get_departments(request:Request, db: AsyncSession = Depends(get_db)):
    return await get_all_departments(db)


@router.get("/", name="departments", response_model=List[schemas.DepartmentOut])
async def get_template_departments(request:Request, db: AsyncSession = Depends(get_db)):
    departments = await get_all_departments(db)
    
    return templates.TemplateResponse("dashboard/departments.html", {"request": request, "data": departments})


async def get_department_by_id(id: int,db: AsyncSession):
    query = select(models.Department).where(models.Department.id ==id)
    result = await db.execute(query)
    return result.scalar_one()

@router.get("/{id}", response_model=schemas.DepartmentOut)
async def get_department(id: int, db: AsyncSession = Depends(get_db)):
    department = await get_department_by_id(id,db)
   
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id: {id} doesn not exist")
    
    return department

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(id: int, db: AsyncSession = Depends(get_db)):
    department = await get_department_by_id(id,db)
    
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id:{id} doesn't exist")
    
    query = delete(models.Department).where(models.Department.id == id)
    await db.execute(query)
    await db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

