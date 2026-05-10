import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest
from flask import Flask
from unittest.mock import patch

from controller import water_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(water_bp)

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# =====================================================
# TEST /generate
# =====================================================
@patch("controller.generate_sensor_data")
@patch("controller.WaterRepo.insert_water_data")
def test_generate_data(mock_insert, mock_generate, client):

    mock_generate.return_value = {
        "ph": 7.1,
        "ri": 1.33,
        "tds": 120,
        "turbidity": 4,
        "water_level": 80,
    }

    response = client.get("/generate")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Random sensor data generated"
    }

    mock_insert.assert_called_once()


# =====================================================
# TEST /report/basic SUCCESS
# =====================================================
@patch("controller.WaterService.basic_report")
@patch("controller.WaterRepo.get_latest")
def test_basic_report_success(
    mock_get_latest,
    mock_basic_report,
    client
):

    mock_get_latest.return_value = (
        7.0,
        1.33,
        120,
        4,
        80,
        "2026-05-10"
    )

    mock_basic_report.return_value = {
        "status": "safe",
        "message": "Water is safe",
        "ri": 1.33,
    }

    response = client.get("/report/basic")

    assert response.status_code == 200
    assert response.get_json()["status"] == "safe"


# =====================================================
# TEST /report/basic NO DATA
# =====================================================
@patch("controller.WaterRepo.get_latest")
def test_basic_report_no_data(
    mock_get_latest,
    client
):

    mock_get_latest.return_value = None

    response = client.get("/report/basic")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "No data available"
    }


# =====================================================
# TEST /report/advanced SUCCESS
# =====================================================
@patch("controller.WaterService.advanced_report")
@patch("controller.WaterRepo.get_latest")
def test_advanced_report_success(
    mock_get_latest,
    mock_advanced_report,
    client
):

    mock_get_latest.return_value = (
        7.0,
        1.33,
        120,
        4,
        80,
        "2026-05-10"
    )

    mock_advanced_report.return_value = {
        "quality": "good"
    }

    response = client.get("/report/advanced")

    assert response.status_code == 200
    assert response.get_json()["quality"] == "good"


# =====================================================
# TEST /report/advanced NO DATA
# =====================================================
@patch("controller.WaterRepo.get_latest")
def test_advanced_report_no_data(
    mock_get_latest,
    client
):

    mock_get_latest.return_value = None

    response = client.get("/report/advanced")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "No data available"
    }


# =====================================================
# TEST /latest SUCCESS
# =====================================================
@patch("controller.WaterRepo.get_latest")
def test_latest_success(
    mock_get_latest,
    client
):

    mock_get_latest.return_value = (
        7.0,
        1.33,
        120,
        4,
        80,
        "2026-05-10"
    )

    response = client.get("/latest")

    data = response.get_json()

    assert response.status_code == 200
    assert data["ph"] == 7.0
    assert data["ri"] == 1.33
    assert data["tds"] == 120
    assert data["turbidity"] == 4
    assert data["water_level"] == 80


# =====================================================
# TEST /latest NO DATA
# =====================================================
@patch("controller.WaterRepo.get_latest")
def test_latest_no_data(
    mock_get_latest,
    client
):

    mock_get_latest.return_value = None

    response = client.get("/latest")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "No data available"
    }


# =====================================================
# TEST /trend SUCCESS
# =====================================================
@patch("controller.WaterRepo.get_recent")
def test_trend_success(
    mock_get_recent,
    client
):

    mock_get_recent.return_value = [
        (
            7.0,
            1.33,
            120,
            4,
            80,
            "2026-05-10"
        ),
        (
            7.2,
            1.34,
            125,
            5,
            78,
            "2026-05-11"
        ),
    ]

    response = client.get("/trend?limit=2")

    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 2
    assert len(data["points"]) == 2


# =====================================================
# TEST /trend INVALID LIMIT
# =====================================================
@patch("controller.WaterRepo.get_recent")
def test_trend_invalid_limit(
    mock_get_recent,
    client
):

    mock_get_recent.return_value = []

    response = client.get("/trend?limit=abc")

    assert response.status_code == 200

    mock_get_recent.assert_called_once_with(30)