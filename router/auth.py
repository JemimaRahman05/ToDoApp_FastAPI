from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Annotated,Optional
from database import SessionLocal
from models import Users
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY ='86746eeb8285ca279c6251e0bd83cdd50c88027b934a93f19d8b9af782139516'
ALGORITHM = 'HS256' 

class CreateUsers(BaseModel):
    email : str
    username : str
    firstname : str
    lastname : str
    password : str
    role : str
    phone_number: str  


class UpdateUsers(BaseModel):
    email : Optional[str] = Field(default=None)
    username : Optional[str] = Field(default=None)
    firstname : Optional[str] = Field(default=None)
    lastname : Optional[str]= Field(default=None)
    phone_number: Optional[str] = Field(default=None)

class UpdatePassword(BaseModel):
    current_password:str
    new_password:str

def authenticate_user(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password, user.hash_password):
        return user
    return False

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail='User not found')
        return {'username': username, 'id': user_id, 'role': role}
    except:
        raise HTTPException(status_code=404, detail='User not found')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@router.post('/createuser')
def create_users(db : db_dependency, new_user : CreateUsers):
    user_model = Users(
        email = new_user.email,
        username = new_user.username,
        firstname = new_user.firstname,
        lastname = new_user.lastname,
        hash_password = bcrypt_context.hash(new_user.password),
        is_active = True,
        role = new_user.role,
        phone_number= new_user.phone_number
    )

    db.add(user_model)
    db.commit()

    return JSONResponse(status_code=201, content={'message' : 'User created successfully'})


@router.post('/login')
def login_user(db : db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    user = authenticate_user(form_data.username, form_data.password, db) 
    if not user: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
    
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    return {'access_token': token, 'tokey_type': 'bearer'}


@router.put('/edituser')
def update_use(user: user_dependency, db : db_dependency, update_user: UpdateUsers):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
    
    user = db.query(Users).filter(Users.id == user.get('id')).first()
    
    update_data = update_user.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(user,key,value)
    
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'User updated successfully'})

@router.put('/passwordchange')
def update_password(user: user_dependency, db : db_dependency, update_password: UpdatePassword):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
    
    user = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(update_password.current_password,user.hash_password):
        return JSONResponse(status_code=200, content={'message' : 'Password is wrong'})
    user.hash_password=bcrypt_context.hash(update_password.new_password)
    db.add(user)
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Password updated successfully'})
