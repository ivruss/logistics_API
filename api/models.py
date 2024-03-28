import os

from pydantic import BaseModel
from sqlalchemy import (
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

metadata = MetaData()


location = Table(
    "location",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("zip", Integer, unique=True),
    Column("city", String),
    Column("state", String),
    Column("latitude", Float),
    Column("longitude", Float),
)


class Location(BaseModel):
    zip: int
    city: str
    state: str
    latitude: float
    longitude: float


cargo = Table(
    "cargo",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("weight", Integer),
    Column("description", String),
    Column("pickup_location", ForeignKey("location.zip")),
    Column("delivery_location", ForeignKey("location.zip")),
    CheckConstraint("weight < 1000"),
    CheckConstraint("weight > 0"),
)


class Cargo(BaseModel):
    weight: str
    description: str
    pickup_location: str
    delivery_location: str


car = Table(
    "car",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("license_plate", String),
    Column("current_location", ForeignKey("location.zip")),
    Column("capacity", Integer),
    CheckConstraint("capacity < 1000"),
    CheckConstraint("capacity > 0"),
)


class Car(BaseModel):
    license_plate: str
    current_location: int
    capacity: int
