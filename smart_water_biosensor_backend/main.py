from flask import Flask
from flasgger import Swagger
from controller import water_bp
from models import create_table

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)