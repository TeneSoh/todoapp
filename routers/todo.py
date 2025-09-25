from typing import Annotated
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
# from fastapi import Depends, FastAPI, HTTPException, Path, status, APIRouter
from fastapi import Depends, HTTPException, Path, APIRouter
from models import Base
from models import Todos
from starlette import status
from routers.auth import get_current_user
# import todoapp.routers.auth as auth

from todoapp.database import engine, SessionLocal


routers = APIRouter(prefix="/todo", tags=["todo"])

# request validation 
class TodoRequest(BaseModel):
    title:str
    description:str
    priority:int
    complete:bool

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)

# app.include_router(auth.routers)
# creer toutes les tables du models
Base.metadata.create_all(bind=engine)

# creer la dependance de notre base de donnee
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# on utilise ici query() a la blace de object en django

db_dependency =  Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@routers.get("/")
async def read_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@routers.get('/{todo_id}')
async def read_todo(db:db_dependency, todo_id:int, user: user_dependency):
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get('id')).first()
    if todo is not None:
        return todo

    raise HTTPException(status_code=404, detail="ressource not found")

@routers.post('/create-todo', status_code=status.HTTP_201_CREATED)
async def store(db:db_dependency, request:TodoRequest, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    todo = Todos(**request.model_dump(), owner_id = user['id'])
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@routers.put('/todo-edit/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def edit(user:user_dependency , db:db_dependency, request:TodoRequest, todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    todo_item = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get('id')).first()
    if todo_item is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_item.title = request.title # type: ignore
    todo_item.description = request.description # type: ignore
    todo_item.priority = request.priority # type: ignore
    todo_item.complete = request.complete # type: ignore
    db.commit()
    db.refresh(todo_item)
    return todo_item

@routers.delete('/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete(user: user_dependency, db: db_dependency, todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    todelet = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get('id')).first()
    if todelet is None:
        raise HTTPException(status_code=404, detail='ressource not found')
    
    db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get('id')).delete()

    db.commit()