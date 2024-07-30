from pydantic import BaseModel, Field, HttpUrl
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID


class OtherModelBase(BaseModel):
    field_str: str = Field(max_length=100)


class OtherModelCreate(OtherModelBase):
    pass


class OtherModel(OtherModelBase):
    id: int

    class Config:
        orm_mode = True


class ItemBase(BaseModel):
    field_boolean: bool
    field_str: str = Field(title="field str", max_length=200)
    field_date: date | None = None
    field_datetime: datetime
    field_decimal: Decimal | None = None
    field_integer: int | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True
