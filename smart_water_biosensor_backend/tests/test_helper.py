import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from helper import generate_sensor_data
from dto import WaterDTO


# =====================================================
# TEST RETURN TYPE
# =====================================================
def test_generate_sensor_data_returns_waterdto():

    data = generate_sensor_data()

    assert isinstance(data, WaterDTO)


# =====================================================
# TEST PH RANGE
# =====================================================
def test_generate_sensor_data_ph_range():

    data = generate_sensor_data()

    assert 6.5 <= data.ph <= 8.5


# =====================================================
# TEST RI RANGE
# =====================================================
def test_generate_sensor_data_ri_range():

    data = generate_sensor_data()

    assert 1.30 <= data.ri <= 1.40


# =====================================================
# TEST TDS RANGE
# =====================================================
def test_generate_sensor_data_tds_range():

    data = generate_sensor_data()

    assert 50 <= data.tds <= 500


# =====================================================
# TEST TURBIDITY RANGE
# =====================================================
def test_generate_sensor_data_turbidity_range():

    data = generate_sensor_data()

    assert 0 <= data.turbidity <= 10


# =====================================================
# TEST WATER LEVEL RANGE
# =====================================================
def test_generate_sensor_data_water_level_range():

    data = generate_sensor_data()

    assert 10 <= data.water_level <= 100


# =====================================================
# TEST ALL ATTRIBUTES EXIST
# =====================================================
def test_generate_sensor_data_attributes():

    data = generate_sensor_data()

    assert hasattr(data, "ph")
    assert hasattr(data, "ri")
    assert hasattr(data, "tds")
    assert hasattr(data, "turbidity")
    assert hasattr(data, "water_level")