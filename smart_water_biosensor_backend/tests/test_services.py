import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from services import WaterService


# =====================================================
# TEST is_ri_safe TRUE
# =====================================================
def test_is_ri_safe_true():

    result = WaterService.is_ri_safe(1.34)

    assert result is True


# =====================================================
# TEST is_ri_safe FALSE BELOW RANGE
# =====================================================
def test_is_ri_safe_false_below():

    result = WaterService.is_ri_safe(1.20)

    assert result is False


# =====================================================
# TEST is_ri_safe FALSE ABOVE RANGE
# =====================================================
def test_is_ri_safe_false_above():

    result = WaterService.is_ri_safe(1.40)

    assert result is False


# =====================================================
# TEST basic_report PASS
# =====================================================
def test_basic_report_pass():

    data = (
        7.0,        # ph
        1.34,       # ri
        120,        # tds
        4,          # turbidity
        80,         # water_level
        "2026-05-10"
    )

    result = WaterService.basic_report(data)

    assert result["status"] == "PASS"
    assert result["message"] == "Water is drinkable (Basic)"
    assert result["ri"] == 1.34


# =====================================================
# TEST basic_report FAIL
# =====================================================
def test_basic_report_fail():

    data = (
        7.0,
        1.50,
        120,
        4,
        80,
        "2026-05-10"
    )

    result = WaterService.basic_report(data)

    assert result["status"] == "FAIL"
    assert result["message"] == "Water is NOT drinkable (RI failed)"
    assert result["ri"] == 1.50


# =====================================================
# TEST advanced_report PASS
# =====================================================
def test_advanced_report_pass():

    data = (
        7.2,
        1.34,
        140,
        3,
        85,
        "2026-05-10"
    )

    result = WaterService.advanced_report(data)

    assert result["status"] == "PASS"
    assert result["message"] == "Water is drinkable (Advanced)"

    assert result["data"]["ph"] == 7.2
    assert result["data"]["ri"] == 1.34
    assert result["data"]["tds"] == 140
    assert result["data"]["turbidity"] == 3
    assert result["data"]["water_level"] == 85


# =====================================================
# TEST advanced_report FAIL
# =====================================================
def test_advanced_report_fail():

    data = (
        7.2,
        1.50,
        140,
        3,
        85,
        "2026-05-10"
    )

    result = WaterService.advanced_report(data)

    assert result["status"] == "FAIL"
    assert result["message"] == "Water is NOT drinkable (RI failed)"
    assert result["ri"] == 1.50