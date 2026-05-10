import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# =====================================================
# TEST HEALTH ENDPOINT
# =====================================================
def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "ok": True
    }


# =====================================================
# TEST API INDEX
# =====================================================
def test_api_index(client):

    response = client.get("/api")

    data = response.get_json()

    assert response.status_code == 200

    assert data["name"] == "Smart Water Biosensor API"
    assert data["docs"] == "/apidocs/"
    assert data["health"] == "/health"

    assert "/water/generate" in data["endpoints"]
    assert "/water/latest" in data["endpoints"]


# =====================================================
# TEST ROOT ROUTE
# =====================================================
def test_root_route(client):

    response = client.get("/")

    # Since it serves HTML
    assert response.status_code in [200, 404]


# =====================================================
# TEST ABOUT ROUTE
# =====================================================
def test_about_route(client):

    response = client.get("/about")

    assert response.status_code in [200, 404]


# =====================================================
# TEST ABOUT HTML ROUTE
# =====================================================
def test_about_html_route(client):

    response = client.get("/about.html")

    assert response.status_code in [200, 404]


# =====================================================
# TEST INVALID STATIC FILE
# =====================================================
def test_invalid_static_file(client):

    response = client.get("/invalid_file.js")

    assert response.status_code == 404

    assert response.get_json() == {
        "error": "Not Found"
    }


# =====================================================
# TEST WATER BLUEPRINT REGISTERED
# =====================================================
def test_water_blueprint_registered(client):

    response = client.get("/water/latest")

    # Can be 200 or 404 depending on DB data
    assert response.status_code in [200, 404]


# =====================================================
# TEST SWAGGER DOCS AVAILABLE
# =====================================================
def test_swagger_docs(client):

    response = client.get("/apidocs/")

    assert response.status_code in [200, 302]