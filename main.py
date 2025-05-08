from flask import Flask
from flask_cors import CORS
from routes.sensor_routes import sensor_bp
import os

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Registrar el blueprint de sensores
app.register_blueprint(sensor_bp, url_prefix='/api')

if __name__ == '__main__':
    # Obtener el puerto del entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    # En producción, no usar debug
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
