from models import get_connection

class WaterRepo:

    @staticmethod
    def insert_water_data(dto):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO water_data (ph, ri, tds, turbidity, water_level)
            VALUES (?, ?, ?, ?, ?)
        """, (dto.ph, dto.ri, dto.tds, dto.turbidity, dto.water_level))

        conn.commit()
        conn.close()

    @staticmethod
    def get_latest():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ph, ri, tds, turbidity, water_level, created_at
            FROM water_data
            ORDER BY id DESC LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        return row