import sys
import os
import sqlite3

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from models import get_connection, create_table, DB_NAME


# =====================================================
# TEST DATABASE CONNECTION
# =====================================================
def test_get_connection():

    conn = get_connection()

    assert conn is not None
    assert isinstance(conn, sqlite3.Connection)

    conn.close()


# =====================================================
# TEST TABLE CREATION
# =====================================================
def test_create_table():

    # Create table
    create_table()

    # Connect to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check table exists
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='water_data'
    """)

    table = cursor.fetchone()

    conn.close()

    assert table is not None
    assert table[0] == "water_data"


# =====================================================
# TEST TABLE COLUMNS
# =====================================================
def test_water_data_table_columns():

    create_table()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(water_data)")

    columns = cursor.fetchall()

    conn.close()

    column_names = [column[1] for column in columns]

    expected_columns = [
        "id",
        "ph",
        "ri",
        "tds",
        "turbidity",
        "water_level",
        "created_at"
    ]

    for column in expected_columns:
        assert column in column_names