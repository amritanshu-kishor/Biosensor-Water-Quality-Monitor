import random
from dto import WaterDTO

def generate_sensor_data():
    return WaterDTO(
        ph=round(random.uniform(6.5, 8.5), 2),
        ri=round(random.uniform(1.30, 1.40), 4),
        tds=round(random.uniform(50, 500), 2),
        turbidity=round(random.uniform(0, 10), 2),
        water_level=round(random.uniform(10, 100), 2)
    )