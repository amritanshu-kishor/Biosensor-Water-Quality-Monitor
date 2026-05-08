class WaterService:

    @staticmethod
    def is_ri_safe(ri):
        # Example condition
        return 1.33 <= ri <= 1.35

    @staticmethod
    def basic_report(data):
        ph, ri, tds, turbidity, water_level, created_at = data

        if not WaterService.is_ri_safe(ri):
            return {
                "status": "FAIL",
                "message": "Water is NOT drinkable (RI failed)",
                "ri": ri
            }

        return {
            "status": "PASS",
            "message": "Water is drinkable (Basic)",
            "ri": ri
        }

    @staticmethod
    def advanced_report(data):
        ph, ri, tds, turbidity, water_level, created_at = data

        if not WaterService.is_ri_safe(ri):
            return {
                "status": "FAIL",
                "message": "Water is NOT drinkable (RI failed)",
                "ri": ri
            }

        return {
            "status": "PASS",
            "message": "Water is drinkable (Advanced)",
            "data": {
                "ph": ph,
                "ri": ri,
                "tds": tds,
                "turbidity": turbidity,
                "water_level": water_level,
                "timestamp": created_at
            }
        }