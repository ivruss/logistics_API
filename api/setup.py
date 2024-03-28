import csv
import random
import string

from models import Location, Car, engine, metadata
from serializers import LocationTable, CarTable

class CarsGenerator():
    """Класс-генератор для создания 20 машин при запуске программы"""
    
    def _generate_license_plate(self):
        """Генерируем случайный номер машины"""
        
        number = random.randint(1000, 9999)
        letter = random.choice(string.ascii_uppercase)
        return f"{number}{letter}"
    
    def _generate_capacity(self):
        """Генерируем случайную грузоподъемность"""
        
        return random.randint(1, 999)


    def generate(self, zips):
        """Генерируем данные для 20 машин"""
        
        data = []
        for _ in range(20):
            
            license_plate = self._generate_license_plate()
            location = random.choice(zips)
            capacity = self._generate_capacity()
            data.append(Car(license_plate=license_plate, current_location=location, capacity=capacity))

        return data


def setup():
    """Функция первичного заполнения БД"""
    
    metadata.create_all(engine)   
    
    with engine.connect() as conn:
        loc_table = LocationTable(conn)
        cars_table = CarTable(conn)
        gen = CarsGenerator()

        with open("data/uszips.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            zips = []
            
            for row in reader:
                location = Location(
                    zip=row["zip"],
                    city=row["city"],
                    state=row["state_name"],
                    latitude=row["lat"],
                    longitude=row["lng"],
                )
                
                print(f"ZIP #{location.zip}")
                zips.append(location.zip)
                loc_table.post(location)

        
        cars = gen.generate(zips=zips)
        
        for car in cars: 
            cars_table.post(car)     
        
        open("initialized.flag", "w").close()
        print("Флаг заполнения создан")

