from flask import Blueprint, jsonify
from repo import WaterRepo
from services import WaterService
from helper import generate_sensor_data

water_bp = Blueprint("water", __name__)


# @water_bp.route("/generate", methods=["GET"])
# def generate_data():
#     data = generate_sensor_data()
#     WaterRepo.insert_water_data(data)

#     return jsonify({"message": "Random sensor data generated"})

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

# @water_bp.route("/report/basic", methods=["GET"])
# def basic_report():
#     data = WaterRepo.get_latest()

#     if not data:
#         return jsonify({"error": "No data available"}), 404

#     result = WaterService.basic_report(data)
#     return jsonify(result)

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

# @water_bp.route("/report/advanced", methods=["GET"])
# def advanced_report():
#     data = WaterRepo.get_latest()

#     if not data:
#         return jsonify({"error": "No data available"}), 404

#     result = WaterService.advanced_report(data)
#     return jsonify(result)

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