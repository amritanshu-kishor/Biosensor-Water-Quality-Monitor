from flask import Blueprint, jsonify, request
from repo import WaterRepo
from services import WaterService
from helper import generate_sensor_data

water_bp = Blueprint("water", __name__)

@water_bp.route("/generate", methods=["GET"])
def generate_data():
    """
    Generate Random Sensor Data
    ---
    tags:
      - Water Sensor
    responses:
      200:
        description: Random sensor data generated
    """
    data = generate_sensor_data()
    WaterRepo.insert_water_data(data)

    return jsonify({"message": "Random sensor data generated"})

@water_bp.route("/report/basic", methods=["GET"])
def basic_report():
    """
    Get Basic Water Report (RI Only)
    ---
    tags:
      - Water Report
    responses:
      200:
        description: Basic report based on RI
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
            ri:
              type: number
    """
    data = WaterRepo.get_latest()

    if not data:
        return jsonify({"error": "No data available"}), 404

    result = WaterService.basic_report(data)
    return jsonify(result)

@water_bp.route("/report/advanced", methods=["GET"])
def advanced_report():
    """
    Get Advanced Water Report
    ---
    tags:
      - Water Report
    responses:
      200:
        description: Full water quality report
    """
    data = WaterRepo.get_latest()

    if not data:
        return jsonify({"error": "No data available"}), 404

    result = WaterService.advanced_report(data)
    return jsonify(result)

@water_bp.route("/latest", methods=["GET"])
def latest():
    """
    Get Latest Raw Sensor Row
    ---
    tags:
      - Water Sensor
    responses:
      200:
        description: Latest raw sensor row
      404:
        description: No data available
    """
    data = WaterRepo.get_latest()
    if not data:
        return jsonify({"error": "No data available"}), 404

    ph, ri, tds, turbidity, water_level, created_at = data
    return jsonify({
        "ph": ph,
        "ri": ri,
        "tds": tds,
        "turbidity": turbidity,
        "water_level": water_level,
        "timestamp": created_at,
    })


@water_bp.route("/trend", methods=["GET"])
def trend():
    """
    Get Recent Sensor Trend Rows
    ---
    tags:
      - Water Sensor
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 30
        description: Number of most recent rows to return (max 500)
    responses:
      200:
        description: Recent sensor rows in chronological order
    """
    limit_raw = request.args.get("limit", default="30")
    try:
        limit = int(limit_raw)
    except (TypeError, ValueError):
        limit = 30

    rows = WaterRepo.get_recent(limit)
    payload = []
    for ph, ri, tds, turbidity, water_level, created_at in rows:
        payload.append(
            {
                "ph": ph,
                "ri": ri,
                "tds": tds,
                "turbidity": turbidity,
                "water_level": water_level,
                "timestamp": created_at,
            }
        )
    return jsonify({"points": payload, "count": len(payload)})