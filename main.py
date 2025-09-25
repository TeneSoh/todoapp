# from typing import Annotated
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from fastapi import Depends, FastAPI, HTTPException, Path, status
from fastapi import FastAPI
# import models
# from models import Todos
import todoapp.routers.auth as auth
import todoapp.routers.todo as todo

# from database import engine, SessionLocal


app = FastAPI()

# request validation 
# class TodoRequest(BaseModel):
#     title:str
#     description:str
#     priority:int
#     complete:bool

app.include_router(auth.routers)
app.include_router(todo.routers)
# models.Base.metadata.create_all(bind=engine)

