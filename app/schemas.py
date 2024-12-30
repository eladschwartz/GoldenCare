from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List

class UserOut(BaseModel):
   name: str
   id: int
   email : EmailStr
   
   class Config:
     from_attributes = True


class UserLogin(BaseModel):
    email : EmailStr
    password: str
    
      
class UserCreate(BaseModel):
    email : EmailStr
    name: str
    password: str
    department_id: int
    
    
class Token(BaseModel):
    name: str
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
     id: Optional[str] = None
     

class DepartmentOut(BaseModel):
   id: int
   name : str
   
   class Config:
     from_attributes = True
     
class DepartmentCreate(BaseModel):
   name : str
   
class PatientOut(BaseModel):
   id: int
   name : str
   release_date: datetime | None = None
   department_id: int
   
   class Config:
     from_attributes = True
     
class PasswordUpdate(BaseModel):
    user_id: int
    new_password:str
    
        
class PatientCreate(BaseModel):
   name : str
   release_date: datetime | None = None
   department_id: int
   
   
class TreatmentOut(BaseModel):
   id: int
   patient_id: int
   therapist_id: int
   timestamp: datetime
 
   class Config:
     from_attributes = True
     
class TreatmentCreate(BaseModel):
   patient_id: int
   therapist_id: int
   timestamp: datetime
   
   class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
   
class TreatmentCopyRequest(BaseModel):
    therapist_id: int
    from_date: datetime
    to_date: datetime

   
class TableData(BaseModel):
    headers: List[str]
    rows: List[List[str]]
    last_updated: Optional[datetime] = None

    # Pre-validator for rows
    @field_validator('rows', mode='before')
    @classmethod
    def validate_rows(cls, v):
        """
        This validator runs BEFORE type conversion (mode='before')
        Useful for cleaning/preparing raw input data.
        """
        if not isinstance(v, list):
            raise ValueError('Rows must be a list')
        
        # Clean and validate each row
        validated_rows = []
        for row in v:
            # Handle single values by converting to list
            if not isinstance(row, list):
                row = [str(row)]
            
            # Clean each cell in the row
            cleaned_row = []
            for cell in row:
                # Convert to string and clean
                cell_str = str(cell) if cell is not None else ""
                cleaned_str = cell_str.strip()
                cleaned_row.append(cleaned_str)
            
            # Only add rows that aren't completely empty
            if any(cell != "" for cell in cleaned_row):
                validated_rows.append(cleaned_row)
        
        return validated_rows

    # Pre-validator for headers
    @field_validator('headers', mode='before')
    @classmethod
    def validate_headers(cls, v):
        """
        Clean and validate headers before type conversion
        """
        if not isinstance(v, list):
            raise ValueError('Headers must be a list')
        
        # Clean headers and remove empty ones
        cleaned_headers = []
        for header in v:
            header_str = str(header).strip()
            if header_str:  # Only include non-empty headers
                cleaned_headers.append(header_str)
        
        if not cleaned_headers:
            raise ValueError('At least one header is required')
            
        return cleaned_headers

    # Post-validator for checking dimensions
    @field_validator('rows')
    @classmethod
    def check_dimensions(cls, v, info):
        """
        This validator runs AFTER type conversion
        Uses info.data to access other fields
        """
        headers = info.data.get('headers', [])
        if headers:
            for idx, row in enumerate(v):
                if len(row) > len(headers):
                    raise ValueError(
                        f'Row {idx} has more columns ({len(row)}) '
                        f'than headers ({len(headers)})'
                    )
        return v


    class Config:
        json_schema_extra = {
            "example": {
                "headers": ["Time", "Value"],
                "rows": [["08:00", "Value 1"], ["08:15", "Value 2"]]
            }
        }