from . import crud, models, sql_schemas
from .database import SessionLocal, engine
from .models import Item
from fastapi import APIRouter
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session


router = APIRouter()


sql_schemas.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/items/create/", response_model=models.Item)
def create_item(item: models.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.get_item_by_str(db, item.field_str)
    if db_item:
        raise HTTPException(
            status_code=400, detail="Item with such field_str already exists"
        )
    return crud.create_item(db=db, item=item)


@router.post("/items/{item_id}")
def edit_item(item_id: int):
    return {"item_id": item_id}
