import datetime
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from models import Users
from typing import Annotated
from passlib.context import CryptContext
from starlette import status
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
import secrets


# ici on utilse les routes
# app = FastAPI()
routers = APIRouter(prefix="/auth", tags=["auth"])

jwt_secret = secrets.token_urlsafe(64)

SECRET_KEY = jwt_secret
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login/")

class UserRequest(BaseModel):
    email:str
    username:str
    first_name:str
    last_name:str
    password:str
    role:str

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username:str, password:str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

async def create_access_token(username:str, id:int, expire_minutes:int = 30):
    payload = {"sub": username, "id": id, "scope":"access_token"}
    expire = datetime.now(timezone.utc) + timedelta(minutes= expire_minutes)
    payload.update({"exp": expire})
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return access_token

async def create_refresh_token(username:str, id:int, expire_day:int = 7):
    payload = {"sub": username, "id": id, "scope":"refresh_token"}
    expire = datetime.now(timezone.utc) + timedelta(days=expire_day)
    payload.update({"exp": expire})
    refresh_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'access_token':
            username = payload['sub']
            user_id = payload['id']
            return {"username": username, "id": user_id}
        raise HTTPException(status_code=401, detail="Invalid scope for token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

db_dependency = Annotated[Session, Depends(get_db)]

@routers.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency ,data:UserRequest):
    user = Users(
        email = data.email,
        username = data.username,
        first_name = data.first_name,
        last_name = data.last_name,
        # hashed_password = data.password,
        hashed_password = bcrypt_context.hash(data.password),
        role = data.role,
        is_active = True
    )
    print(user)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user": user}
    # return {"user":"hello !!!!"}


@routers.post('/login/')
async def login_for_access_token(db:db_dependency, form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code = 404, detail="invalide credentials" )
    access_token = await create_access_token(user.username, user.id, 30) # type: ignore
    refresh_token = await create_refresh_token(user.username, user.id, 7) # type: ignore
    # return form_data.username
    return {"user": user,"access_token": access_token, "refresh_token": refresh_token, "token_type":"bearer"}