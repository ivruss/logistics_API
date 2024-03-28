import os

from fastapi import FastAPI

from serializers import CarTable, CargoTable, LocationTable
from models import engine, Cargo, Car, Location
from setup import setup

app = FastAPI()

def check_initialization_flag():
    flag_file = "initialized.flag"
    if os.path.exists(flag_file):
        print("База данных уже заполнена. Заполнение не требуется")
        return 0
    
    else:
        print("Необходимо первичное заполнение БД. Пожалуйста, подождите")
        setup()
        return 0
    
check_initialization_flag()

@app.get("/locations")
def get_locs():
    with engine.connect() as conn:
        table = LocationTable(conn)
        data = table.get()
    
    return data


@app.get("/cargos/{cargo_id}")
def get_cargo(cargo_id):
    with engine.connect() as conn:
        table = CargoTable(conn)
        q = table.get_single(cargo_id)
    
    return q


@app.get("/cargos/")
def get_cargos():
    with engine.connect() as conn:
        table = CargoTable(conn)
        q = table.get_all()
    
    return q


@app.post("/cargos/")
def post_cargo(payload: Cargo):
    with engine.connect() as conn:
        table = CargoTable(conn)
        r = table.post(payload)
    
    return r


@app.patch("/cargos/{cargo_id}")
def patch_cargo(cargo_id, payload: dict):
    with engine.connect() as conn:
        table = CargoTable(conn)
        ans = table.update(cargo_id, payload)
        
    return 200

@app.delete("/cargos/{cargo_id}")
def delete_cargo(cargo_id):
    with engine.connect() as conn:
        table = CargoTable(conn)
        ans = table.delete(cargo_id)
    
    return 200