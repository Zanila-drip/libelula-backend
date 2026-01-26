from .fuzzy_service import FuzzyService
import logging

logger = logging.getLogger(__name__)

class SensorService:
    def __init__(self):
        self.sensor_data = []
        self.fuzzy_service = FuzzyService()

    def save_data(self, data):
        """
        Guarda los datos del sensor y evalúa las condiciones
        """
        logger.info(f"Evaluando condiciones para datos: {data}")
        
        # Evaluar condiciones con lógica difusa
        evaluation = self.fuzzy_service.evaluate_conditions(
            data['temperatura'],
            data['humedad'],
            data['humedadSuelo'],
            data['luz']
        )
        
        logger.info(f"Evaluación generada: {evaluation}")
        
        # Agregar evaluación a los datos
        data['evaluacion'] = evaluation
        self.sensor_data.append(data)
        return True

    def get_all_data(self):
        """
        Retorna todos los datos almacenados
        """
        return self.sensor_data

    def get_latest_evaluation(self):
        """
        Retorna la última evaluación realizada
        """
        if self.sensor_data:
            evaluation = self.sensor_data[-1]['evaluacion']
            logger.info(f"Retornando última evaluación: {evaluation}")
            return evaluation
        logger.warning("No hay datos disponibles para evaluación")
        return None 