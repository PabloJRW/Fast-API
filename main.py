from fastapi import FastAPI, Depends, HTTPException, Path
import models
from models import Todos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int =Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, datail="ToDo not found.")


class TodoRequest(BaseModel):
    title:str = Field(min_length=5)
    description:str = Field(min_length=10, max_length=100)
    priority:int = Field(gt=0, lt=5)
    complete:bool 


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.dict())

    db.add(todo_model)
    db.commit()    

