import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flasgger import Swagger
from controller import water_bp
from models import create_table

app = Flask(__name__)
app.url_map.strict_slashes = False

# Allow frontend (static server / file) to call API during dev.
CORS(app)

# Frontend (served by Flask)
FRONT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "front_biosensor"))

# Swagger Config
app.config['SWAGGER'] = {
    'title': 'Smart Water Biosensor API',
    'uiversion': 3
}

swagger = Swagger(app)

# Initialize DB
create_table()

# Register Routes
app.register_blueprint(water_bp, url_prefix="/water")

@app.get("/")
def root():
    # Serve frontend dashboard
    return send_from_directory(FRONT_DIR, "index.html")

@app.get("/api")
def api_index():
    return jsonify(
        {
            "name": "Smart Water Biosensor API",
            "docs": "/apidocs/",
            "health": "/health",
            "endpoints": [
                "/water/generate",
                "/water/latest",
                "/water/report/basic",
                "/water/report/advanced",
            ],
            "frontend": {
                "dashboard": "/",
                "about": "/about.html",
            },
        }
    )

@app.get("/about")
def about_redirect():
    return send_from_directory(FRONT_DIR, "about.html")

@app.get("/about.html")
def about():
    return send_from_directory(FRONT_DIR, "about.html")

@app.get("/<path:path>")
def serve_frontend_files(path: str):
    # Serve static frontend files (app.js, styles.css, assets/*, etc.)
    candidate = os.path.join(FRONT_DIR, path)
    if os.path.isfile(candidate):
        return send_from_directory(FRONT_DIR, path)
    return jsonify({"error": "Not Found"}), 404

@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)