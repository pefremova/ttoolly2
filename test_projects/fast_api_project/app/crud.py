from sqlalchemy.orm import Session

from . import models, sql_schemas


def get_item(db: Session, item_id: int):
    return db.query(sql_schemas.Item).filter(sql_schemas.Item.id == item_id).first()


def get_item_by_str(db: Session, item_str: str):
    return (
        db.query(sql_schemas.Item)
        .filter(sql_schemas.Item.field_str == item_str)
        .first()
    )


def create_item(db: Session, item: models.ItemCreate):
    db_item = sql_schemas.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
