from flask import Blueprint, request, jsonify
from services.sensor_service import SensorService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sensor_bp = Blueprint('sensor', __name__)
sensor_service = SensorService()

@sensor_bp.route('/sensors', methods=['POST'])
def save_sensor_data():
    try:
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Guardar datos y obtener evaluación
        sensor_service.save_data(data)
        
        # Obtener la última evaluación
        evaluation = sensor_service.get_latest_evaluation()
        logger.info(f"Evaluación generada: {evaluation}")
        
        # Devolver mensaje y evaluación
        response = {
            "message": "Datos almacenados",
            "evaluacion": evaluation
        }
        logger.info(f"Respuesta enviada: {response}")
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error al procesar datos: {str(e)}")
        return jsonify({"error": str(e)}), 400

@sensor_bp.route('/sensors', methods=['GET'])
def get_sensor_data():
    try:
        data = sensor_service.get_all_data()
        logger.info(f"Datos almacenados: {data}")
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error al obtener datos: {str(e)}")
        return jsonify({"error": str(e)}), 400

@sensor_bp.route('/sensors/evaluation', methods=['GET'])
def get_evaluation():
    try:
        evaluation = sensor_service.get_latest_evaluation()
        if evaluation:
            return jsonify(evaluation), 200
        return jsonify({"message": "No hay datos disponibles"}), 404
    except Exception as e:
        logger.error(f"Error al obtener evaluación: {str(e)}")
        return jsonify({"error": str(e)}), 400

@sensor_bp.route('/sensors/pump', methods=['GET'])
def get_pump_recommendation():
    try:
        # Obtener los últimos datos
        data = sensor_service.get_all_data()
        if not data:
            return jsonify({"message": "No hay datos disponibles"}), 404
        
        # Obtener la última lectura
        latest_data = data[-1]
        
        # Evaluar si se debe activar la bomba
        pump_evaluation = sensor_service.fuzzy_service.should_activate_pump(
            latest_data['temperatura'],
            latest_data['humedad'],
            latest_data['humedadSuelo'],
            latest_data['luz']
        )
        
        return jsonify(pump_evaluation), 200
    except Exception as e:
        logger.error(f"Error al obtener recomendación de bomba: {str(e)}")
        return jsonify({"error": str(e)}), 400 