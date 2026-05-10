import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from dto import WaterDTO


# =====================================================
# TEST DTO INITIALIZATION
# =====================================================
def test_water_dto_initialization():

    dto = WaterDTO(
        ph=7.2,
        ri=1.33,
        tds=120,
        turbidity=4,
        water_level=85
    )

    assert dto.ph == 7.2
    assert dto.ri == 1.33
    assert dto.tds == 120
    assert dto.turbidity == 4
    assert dto.water_level == 85


# =====================================================
# TEST DTO WITH DIFFERENT VALUES
# =====================================================
def test_water_dto_different_values():

    dto = WaterDTO(
        ph=6.5,
        ri=1.40,
        tds=250,
        turbidity=8,
        water_level=60
    )

    assert dto.ph == 6.5
    assert dto.ri == 1.40
    assert dto.tds == 250
    assert dto.turbidity == 8
    assert dto.water_level == 60


# =====================================================
# TEST DTO TYPES
# =====================================================
def test_water_dto_types():

    dto = WaterDTO(
        ph=7.0,
        ri=1.33,
        tds=100,
        turbidity=2,
        water_level=90
    )

    assert isinstance(dto.ph, float)
    assert isinstance(dto.ri, float)
    assert isinstance(dto.tds, int)
    assert isinstance(dto.turbidity, int)
    assert isinstance(dto.water_level, int)