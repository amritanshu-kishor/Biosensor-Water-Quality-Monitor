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

    @staticmethod
    def get_recent(limit=30):
        conn = get_connection()
        cursor = conn.cursor()

        safe_limit = max(1, min(int(limit), 500))
        cursor.execute(
            """
            SELECT ph, ri, tds, turbidity, water_level, created_at
            FROM water_data
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        )
        rows = cursor.fetchall()
        conn.close()

        # Return in chronological order for plotting.
        return list(reversed(rows))