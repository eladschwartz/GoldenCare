from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, Request, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from .config import settings
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Modified OAuth2 scheme that can read from cookies
class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        # First try getting the token from the authorization header
        authorization = request.headers.get("Authorization")
        if authorization and authorization != 'Bearer null':
            scheme, param = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                return param
     
     
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
                return token[7:]  # Remove 'Bearer ' prefix
            
        # If no token is found, redirect to login page
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/goldencare/login"} 
        )

# Use the modified OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACRESS_TOKEN_EXPIRE_MINTUES = settings.access_token_expire_minutes

def craete_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now() + timedelta(minutes=ACRESS_TOKEN_EXPIRE_MINTUES)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logging.error(f"Token creation error: {str(e)}")
        raise
   
    
def verify_access_token(token:str, credentials_exception):
    try:
        if token is None:
         raise credentials_exception
     
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        id: str = str(payload.get("user_id"))
        
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data

    
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_access_token(token, credentials_exception)
    
    if not token_data:
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            token = token[7:]  # Remove 'Bearer ' prefix
    
    if not token:
        raise credentials_exception
    
    
    return token_data.id


async def get_current_admin(current_user_id: int = Depends(get_current_user),db: AsyncSession = Depends(database.get_db)) -> models.User:
    query = select(models.User).where(models.User.id == current_user_id)
    user = (await db.execute(query)).scalar_one_or_none
    
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user