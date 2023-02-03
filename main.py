from fastapi import FastAPI, Header, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

# Define the SQLAlchemy model for a To-Do item
Base = declarative_base()

class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    is_completed = Column(Integer)

# Connect to the database
engine = create_engine("mysql://user:password@localhost/db_name")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a dependency to create a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the API endpoint to create a new To-Do item
@app.post("/todos")
async def create_todo(item: TodoItem, db=Depends(get_db)):
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id}

# Define the API endpoint to retrieve a list of all To-Do items
@app.get("/todos")
async def read_todos(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    todo_items = db.query(TodoItem).offset(skip).limit(limit).all()
    return {"todos": [{"id": item.id, "task": item.task, "is_completed": item.is_completed} for item in todo_items]}

# Define the API endpoint to retrieve a specific To-Do item by its id
@app.get("/todos/{item_id}")
async def read_todo(item_id: int, db=Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if item is None:
        return {"error": "To-Do item not found"}
    return {"todo": {"id": item.id, "task": item.task, "is_completed": item.is_completed}}

# Define the API endpoint to update a specific To-Do item by its id
@app.put("/todos/{item_id}")
async def update_todo(item_id: int, item: TodoItem, db=Depends(get_db)):
    db_item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if db_item is None:
        return {"error": "To-Do item not found"}
    db_item.task = item.task
    db_item.is_completed = item.is_completed

@app.delete("/todos/{item_id}")
async def delete_todo(item_id: int, db=Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if item is None:
        return {"error": "To-Do item not found"}
    db.delete(item)
    db.commit()
    return {"message": "To-Do item deleted"}
