import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyService:
    def __init__(self):
        # Definir rangos universales
        self.temp_range = np.arange(15, 40, 1)
        self.humidity_range = np.arange(0, 100, 1)
        self.soil_range = np.arange(0, 1023, 1)
        self.light_range = np.arange(0, 1023, 1)

        # Crear conjuntos difusos para temperatura
        self.temperature = ctrl.Antecedent(self.temp_range, 'temperatura')
        self.temperature['fría'] = fuzz.trimf(self.temperature.universe, [15, 15, 25])
        self.temperature['óptima'] = fuzz.trimf(self.temperature.universe, [20, 25, 30])
        self.temperature['caliente'] = fuzz.trimf(self.temperature.universe, [25, 35, 40])

        # Crear conjuntos difusos para humedad ambiente
        self.humidity = ctrl.Antecedent(self.humidity_range, 'humedad')
        self.humidity['baja'] = fuzz.trimf(self.humidity.universe, [0, 0, 50])
        self.humidity['óptima'] = fuzz.trimf(self.humidity.universe, [40, 60, 80])
        self.humidity['alta'] = fuzz.trimf(self.humidity.universe, [70, 100, 100])

        # Crear conjuntos difusos para humedad del suelo
        self.soil = ctrl.Antecedent(self.soil_range, 'suelo')
        self.soil['seco'] = fuzz.trimf(self.soil.universe, [0, 0, 500])
        self.soil['húmedo'] = fuzz.trimf(self.soil.universe, [400, 600, 800])
        self.soil['empapado'] = fuzz.trimf(self.soil.universe, [700, 1023, 1023])

        # Crear conjuntos difusos para luz
        self.light = ctrl.Antecedent(self.light_range, 'luz')
        self.light['baja'] = fuzz.trimf(self.light.universe, [0, 0, 500])
        self.light['óptima'] = fuzz.trimf(self.light.universe, [400, 600, 800])
        self.light['alta'] = fuzz.trimf(self.light.universe, [700, 1023, 1023])

        # Crear variable de salida (estado de la planta)
        self.plant_state = ctrl.Consequent(np.arange(0, 100, 1), 'estado_planta')
        self.plant_state['malo'] = fuzz.trimf(self.plant_state.universe, [0, 0, 40])
        self.plant_state['regular'] = fuzz.trimf(self.plant_state.universe, [30, 50, 70])
        self.plant_state['bueno'] = fuzz.trimf(self.plant_state.universe, [60, 100, 100])

        # Definir reglas
        self.rules = [
            # Reglas para temperatura
            ctrl.Rule(self.temperature['fría'], self.plant_state['malo']),
            ctrl.Rule(self.temperature['óptima'], self.plant_state['bueno']),
            ctrl.Rule(self.temperature['caliente'], self.plant_state['malo']),

            # Reglas para humedad ambiente
            ctrl.Rule(self.humidity['baja'], self.plant_state['malo']),
            ctrl.Rule(self.humidity['óptima'], self.plant_state['bueno']),
            ctrl.Rule(self.humidity['alta'], self.plant_state['regular']),

            # Reglas para humedad del suelo
            ctrl.Rule(self.soil['seco'], self.plant_state['malo']),
            ctrl.Rule(self.soil['húmedo'], self.plant_state['bueno']),
            ctrl.Rule(self.soil['empapado'], self.plant_state['regular']),

            # Reglas para luz
            ctrl.Rule(self.light['baja'], self.plant_state['regular']),
            ctrl.Rule(self.light['óptima'], self.plant_state['bueno']),
            ctrl.Rule(self.light['alta'], self.plant_state['regular'])
        ]

        # Crear sistema de control
        self.plant_ctrl = ctrl.ControlSystem(self.rules)
        self.plant_sim = ctrl.ControlSystemSimulation(self.plant_ctrl)

    def evaluate_conditions(self, temperatura, humedad, suelo, luz):
        """
        Evalúa las condiciones actuales y retorna el estado de la planta
        y recomendaciones
        """
        try:
            # Establecer valores de entrada
            self.plant_sim.input['temperatura'] = float(temperatura)
            self.plant_sim.input['humedad'] = float(humedad)
            self.plant_sim.input['suelo'] = float(suelo)
            self.plant_sim.input['luz'] = float(luz)

            # Calcular resultado
            self.plant_sim.compute()

            # Obtener estado y convertirlo a float normal
            estado = float(self.plant_sim.output['estado_planta'])

            # Generar recomendaciones
            recomendaciones = []
            
            if float(temperatura) < 20:
                recomendaciones.append("La temperatura es muy baja para la planta")
            elif float(temperatura) > 30:
                recomendaciones.append("La temperatura es muy alta para la planta")

            if float(humedad) < 40:
                recomendaciones.append("La humedad ambiente es muy baja")
            elif float(humedad) > 80:
                recomendaciones.append("La humedad ambiente es muy alta")

            if float(suelo) < 400:
                recomendaciones.append("La planta necesita agua")
            elif float(suelo) > 800:
                recomendaciones.append("El suelo está muy húmedo")

            if float(luz) < 400:
                recomendaciones.append("La planta necesita más luz")
            elif float(luz) > 800:
                recomendaciones.append("Hay demasiada luz directa")

            return {
                "estado": round(estado, 2),
                "recomendaciones": recomendaciones,
                "condiciones": {
                    "temperatura": float(temperatura),
                    "humedad": float(humedad),
                    "suelo": float(suelo),
                    "luz": float(luz)
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "estado": 0,
                "recomendaciones": ["Error al evaluar condiciones"],
                "condiciones": {
                    "temperatura": float(temperatura),
                    "humedad": float(humedad),
                    "suelo": float(suelo),
                    "luz": float(luz)
                }
            }

    def should_activate_pump(self, temperatura, humedad, suelo, luz):
        """
        Evalúa si se debe activar la bomba de agua y por cuánto tiempo
        basado en las condiciones actuales
        """
        try:
            # Convertir valores a float
            temp = float(temperatura)
            hum = float(humedad)
            soil = float(suelo)
            light = float(luz)

            # Inicializar variables
            should_activate = False
            reason = []
            tiempo_activacion = 0  # en segundos

            # Verificar suelo (prioridad más alta)
            if soil < 400:  # Suelo seco
                should_activate = True
                reason.append("Suelo seco")
                # Cuanto más seco, más tiempo
                tiempo_activacion += (400 - soil) / 2  # 1 segundo por cada 2 unidades de sequedad
            
            # Verificar temperatura
            if temp > 30:  # Temperatura alta
                should_activate = True
                reason.append("Temperatura alta")
                # Cuanto más alta la temperatura, más tiempo
                tiempo_activacion += (temp - 30) * 2  # 2 segundos por cada grado sobre 30
            
            # Verificar humedad ambiente
            if hum < 40:  # Humedad baja
                should_activate = True
                reason.append("Humedad ambiente baja")
                # Cuanto más baja la humedad, más tiempo
                tiempo_activacion += (40 - hum)  # 1 segundo por cada punto de humedad faltante
            
            # Verificar luz
            if light > 800:  # Mucha luz
                should_activate = True
                reason.append("Exceso de luz")
                # Cuanto más luz, más tiempo
                tiempo_activacion += (light - 800) / 100  # 1 segundo por cada 100 unidades de luz extra

            # Ajustar tiempo mínimo y máximo
            if should_activate:
                tiempo_activacion = max(5, min(60, tiempo_activacion))  # Mínimo 5 segundos, máximo 60 segundos
                tiempo_activacion = round(tiempo_activacion)  # Redondear a segundos enteros

            return {
                "activar": should_activate,
                "tiempo_segundos": tiempo_activacion,
                "razones": reason,
                "condiciones": {
                    "temperatura": temp,
                    "humedad": hum,
                    "suelo": soil,
                    "luz": light
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "activar": False,
                "tiempo_segundos": 0,
                "razones": ["Error al evaluar condiciones"],
                "condiciones": {
                    "temperatura": float(temperatura),
                    "humedad": float(humedad),
                    "suelo": float(suelo),
                    "luz": float(luz)
                }
            } 