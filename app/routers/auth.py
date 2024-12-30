from fastapi import APIRouter, Depends, status, HTTPException,Response
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2
import pandas as pd
from io import BytesIO
from ..schemas import TableData
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["Authentiocation"])

@router.post('/login', response_model=schemas.Token)
def login(user_cerdentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
    print(f"Login attempt for username: {user_cerdentials.username}")
    user = db.query(models.User).filter(models.User.email == user_cerdentials.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentails")
    
    if not utils.verify(user_cerdentials.password, user.password):
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentails")
    
    access_token = oauth2.craete_access_token(data={"user_id": user.id})
    
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer", "name": user.name}
    )
    
    # Set token in cookie as well (belt and suspenders approach)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=18000,
        expires=18000,
        samesite='lax'
    )
    
    return response

@router.post('/logout')
def log_out(response: Response):
      response.delete_cookie(
        key="access_token",
        path="/" 
    )
      
@router.post("/export/excel")
async def export_excel(data: TableData):
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data.rows, columns=data.headers)
    
    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        
        # Get workbook and worksheet objects for formatting
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Add some formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        # Apply header formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Adjust column widths
        for i, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            worksheet.set_column(i, i, max_length + 2)

    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="table_data.xlsx"'
    }
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    