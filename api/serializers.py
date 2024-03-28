from geopy_calc import distance_calc
from models import car, cargo, engine, location
from sqlalchemy import select, join

class LocationTable:
    """Класс для работы с таблицей локаций"""
    
    def __init__(self, conn):
        self.conn = conn

    def post(self, data):
        """Метод создания новой локации"""

        data = data.dict()

        ins = location.insert().values(
            zip=data["zip"],
            city=data["city"],
            state=data["state"],
            latitude=data["latitude"],
            longitude=data["longitude"],
        )

        res = self.conn.execute(ins)
        self.conn.commit()

        return res

    def get(self, amount=None, id=None):
        """Метод получения локации из БД"""
        if id is None:
            query = location.select().limit(amount)
        else:
            query = location.select().where(location.c.id == id)

        q = self.conn.execute(query)
        self.conn.commit()

        keys = ["id", "zip", "city", "state", "latitude", "longitude"]
        res = []

        for item in q.fetchall():
            res.append(dict(zip(keys, item)))

        return res

class CargoTable:
    """Класс для работы с таблицей грузов"""
    
    def __init__(self, conn):
        self.conn = conn

    def post(self, data):
        """Метод добавления груза"""

        data = data.dict()
        
        pickup_loc_q = location.select().where(location.c.zip == data["pickup_location"])
        
        if len(self.conn.execute(pickup_loc_q).fetchall()) == 0:
            return {"Error": "No such location in the database"}
        
        delivery_loc_q = location.select().where(location.c.zip == data["delivery_location"])
        
        if len(self.conn.execute(delivery_loc_q).fetchall()) == 0:
            return {"Error": "No such location in the database"}
        
        ins = cargo.insert().values(
            weight=data["weight"],
            pickup_location=data["pickup_location"],
            delivery_location=data["delivery_location"],
            description=data["description"],
        )

        res = self.conn.execute(ins)
        self.conn.commit()

        return res

    def get_single(self, id=None):
        """Метод получения одного груза"""

        cargo_query = cargo.select().where(cargo.c.id == id)
        q = self.conn.execute(cargo_query)

        keys = ["id", "weight", "description", "pickup_location", "delivery_location"]

        q = q.fetchone()

        if not q:
            return {"code": 404, "details": "cargo with chosen id is not found"}

        res = dict(zip(keys, q))

        cargo_location_q = select(location.c.latitude, location.c.longitude).where(
            location.c.zip == res["pickup_location"]
        )
        cargo_location = self.conn.execute(cargo_location_q).fetchone()

        cars_query = select(car.c.current_location, car.c.license_plate)
        q = self.conn.execute(cars_query)

        keys = ["current_location", "license_plate"]
        cars = []

        for item in q.fetchall():
            car_location_q = select(location.c.latitude, location.c.longitude).where(
                location.c.zip == item[0]
            )
            car_location = self.conn.execute(car_location_q).fetchone()

            dist = distance_calc(cargo_location, car_location)

            car_dict = dict(zip(keys, item))
            car_dict.update({"distance": dist})
            cars.append(car_dict)

        res.update({"cars": cars})

        return res

    def get_all(self):
        join_condition = cargo.c.pickup_location == location.c.zip
        join_query = join(cargo, location, join_condition)
        cargo_q = select(cargo, location).select_from(join_query)

        cargos = self.conn.execute(cargo_q).fetchall()

        keys = [
            "id",
            "weight",
            "description",
            "pickup_location",
            "delivery_location",
            "loc_id",
            "loc_zip",
            "city",
            "state",
            "latitude",
            "longitude",
        ]

        res = []
        for cargo_obj in cargos:
            mixed_dict = dict(zip(keys, cargo_obj))
            # print(mixed_dict)

            cargo_lat, cargo_lng = mixed_dict["latitude"], mixed_dict["longitude"]

            join_condition = car.c.current_location == location.c.zip
            join_query = join(car, location, join_condition)

            cars_query = select(car, location).select_from(join_query)
            cars_info = self.conn.execute(cars_query).fetchall()

            cars = 0
            for car_inst in cars_info:

                dist = distance_calc(car_inst[-2:], (cargo_lat, cargo_lng))

                if dist <= 450:
                    cars += 1

            cargo_dict = dict(zip(keys, list(mixed_dict.values())[:5]))
            cargo_dict.update({"cars near": cars})

            res.append(cargo_dict)

        return res

    def update(self, id, data):
        """Метод изменения информации о грузе"""

        update_query = cargo.update().where(cargo.c.id == id)

        for key, value in data.items():
            self.conn.execute(update_query.values(**{key: value}))

        self.conn.commit()

    def delete(self, id):
        s = cargo.delete().where(cargo.c.id == id)
        
        self.conn.execute(s)
        self.conn.commit()

class CarTable:
    """Класс для работы с таблицей машин"""
    
    def __init__(self, conn):
        self.conn = conn

    def post(self, data):
        """Метод добавления новой машины"""

        data = data.dict()
        
        curr_loc_q = location.select().where(location.c.zip == data["current_location"])
        
        if len(self.conn.execute(curr_loc_q).fetchall()) == 0:
            return {"Error": "No such location in the database"}

        ins = car.insert().values(
            license_plate=data["license_plate"],
            current_location=data["current_location"],
            capacity=data["capacity"],
        )

        res = self.conn.execute(ins)
        self.conn.commit()

        return res.inserted_primary_key[0]

    def get(self, amount=None, id=None):
        """Метод получения информации о машине"""

        if id is None:
            query = car.select().limit(amount)
        else:
            query = car.select().where(car.c.id == id)

        q = self.conn.execute(query)
        self.conn.commit()

        keys = ["id", "license_plate", "current_location", "capacity"]
        res = []

        for item in q.fetchall():
            res.append(dict(zip(keys, item)))

        return res
