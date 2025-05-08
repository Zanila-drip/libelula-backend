from flask import Blueprint, request, jsonify
from services.sensor_service import SensorService
from services.fuzzy_service import FuzzyService
import logging
import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sensor_bp = Blueprint('sensor', __name__)
sensor_service = SensorService()
fuzzy_service = FuzzyService()

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

@sensor_bp.route('/pump', methods=['GET'])
def check_pump():
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
        logger.error(f"Error al verificar estado de la bomba: {str(e)}")
        return jsonify({"error": str(e)}), 400

@sensor_bp.route('/membership-functions', methods=['GET'])
def get_membership_functions():
    """
    Retorna los datos de las funciones de pertenencia para visualización
    """
    try:
        # Obtener datos de temperatura
        temp_data = {
            'range': fuzzy_service.temp_range.tolist(),
            'sets': {
                'fría': fuzzy_service.temperature['fría'].mf.tolist(),
                'óptima': fuzzy_service.temperature['óptima'].mf.tolist(),
                'caliente': fuzzy_service.temperature['caliente'].mf.tolist()
            }
        }

        # Obtener datos de humedad
        humidity_data = {
            'range': fuzzy_service.humidity_range.tolist(),
            'sets': {
                'baja': fuzzy_service.humidity['baja'].mf.tolist(),
                'óptima': fuzzy_service.humidity['óptima'].mf.tolist(),
                'alta': fuzzy_service.humidity['alta'].mf.tolist()
            }
        }

        # Obtener datos de suelo
        soil_data = {
            'range': fuzzy_service.soil_range.tolist(),
            'sets': {
                'seco': fuzzy_service.soil['seco'].mf.tolist(),
                'húmedo': fuzzy_service.soil['húmedo'].mf.tolist(),
                'empapado': fuzzy_service.soil['empapado'].mf.tolist()
            }
        }

        # Obtener datos de luz
        light_data = {
            'range': fuzzy_service.light_range.tolist(),
            'sets': {
                'baja': fuzzy_service.light['baja'].mf.tolist(),
                'óptima': fuzzy_service.light['óptima'].mf.tolist(),
                'alta': fuzzy_service.light['alta'].mf.tolist()
            }
        }

        # Obtener datos de estado de la planta
        plant_state_data = {
            'range': np.arange(0, 100, 1).tolist(),
            'sets': {
                'malo': fuzzy_service.plant_state['malo'].mf.tolist(),
                'regular': fuzzy_service.plant_state['regular'].mf.tolist(),
                'bueno': fuzzy_service.plant_state['bueno'].mf.tolist()
            }
        }

        # Obtener datos de tiempo de bomba
        pump_time_data = {
            'range': np.arange(0, 60, 1).tolist(),
            'sets': {
                'corto': fuzzy_service.pump_time['corto'].mf.tolist(),
                'medio': fuzzy_service.pump_time['medio'].mf.tolist(),
                'largo': fuzzy_service.pump_time['largo'].mf.tolist()
            }
        }

        return jsonify({
            'temperatura': temp_data,
            'humedad': humidity_data,
            'suelo': soil_data,
            'luz': light_data,
            'estado_planta': plant_state_data,
            'tiempo_bomba': pump_time_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500 