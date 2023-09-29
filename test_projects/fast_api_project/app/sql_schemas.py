from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Numeric,
)

from .database import Base


class OtherModel(Base):
    __tablename__ = "other_models"
    id = Column(Integer, primary_key=True, index=True)
    field_str = Column(String(length=100))


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)

    field_boolean = Column(Boolean)
    field_str = Column(String(length=200), unique=True, index=True)
    field_date = Column(Date, nullable=True)
    field_datetime = Column(DateTime)
    field_decimal = Column(Numeric(asdecimal=True, precision=2, scale=6), nullable=True)
    field_integer = Column(Integer, nullable=True)
