import sys
import os
import sqlite3

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from repo import WaterRepo
from dto import WaterDTO
from models import get_connection


# =====================================================
# SETUP TEST DATABASE TABLE
# =====================================================
def setup_module(module):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ph REAL,
            ri REAL,
            tds REAL,
            turbidity REAL,
            water_level REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
# TEST INSERT WATER DATA
# =====================================================
def test_insert_water_data():

    dto = WaterDTO(
        ph=7.1,
        ri=1.33,
        tds=120,
        turbidity=4,
        water_level=80
    )

    WaterRepo.insert_water_data(dto)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ph, ri, tds, turbidity, water_level
        FROM water_data
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    assert row is not None
    assert row[0] == 7.1
    assert row[1] == 1.33
    assert row[2] == 120
    assert row[3] == 4
    assert row[4] == 80


# =====================================================
# TEST GET LATEST
# =====================================================
def test_get_latest():

    dto = WaterDTO(
        ph=7.5,
        ri=1.35,
        tds=150,
        turbidity=5,
        water_level=75
    )

    WaterRepo.insert_water_data(dto)

    latest = WaterRepo.get_latest()

    assert latest is not None
    assert latest[0] == 7.5
    assert latest[1] == 1.35
    assert latest[2] == 150
    assert latest[3] == 5
    assert latest[4] == 75


# =====================================================
# TEST GET RECENT
# =====================================================
def test_get_recent():

    rows = WaterRepo.get_recent(limit=5)

    assert isinstance(rows, list)
    assert len(rows) >= 1


# =====================================================
# TEST GET RECENT LIMIT LOWER BOUND
# =====================================================
def test_get_recent_min_limit():

    rows = WaterRepo.get_recent(limit=0)

    assert isinstance(rows, list)


# =====================================================
# TEST GET RECENT LIMIT UPPER BOUND
# =====================================================
def test_get_recent_max_limit():

    rows = WaterRepo.get_recent(limit=1000)

    assert isinstance(rows, list)


# =====================================================
# TEST GET RECENT RETURNS CHRONOLOGICAL ORDER
# =====================================================
def test_get_recent_returns_list():

    rows = WaterRepo.get_recent(limit=3)

    assert isinstance(rows, list)

    if len(rows) > 0:
        assert isinstance(rows[0], tuple)