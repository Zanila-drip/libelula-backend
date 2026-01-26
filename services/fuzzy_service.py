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

        # Crear variables de salida
        self.plant_state = ctrl.Consequent(np.arange(0, 100, 1), 'estado_planta')
        self.plant_state['malo'] = fuzz.trimf(self.plant_state.universe, [0, 0, 40])
        self.plant_state['regular'] = fuzz.trimf(self.plant_state.universe, [30, 50, 70])
        self.plant_state['bueno'] = fuzz.trimf(self.plant_state.universe, [60, 100, 100])

        self.pump_time = ctrl.Consequent(np.arange(0, 21, 1), 'tiempo_bomba')
        self.pump_time['corto'] = fuzz.trimf(self.pump_time.universe, [3, 5, 7])
        self.pump_time['medio'] = fuzz.trimf(self.pump_time.universe, [7, 10, 14])
        self.pump_time['largo'] = fuzz.trimf(self.pump_time.universe, [13, 17, 20])

        # Definir reglas mejoradas
        self.rules = [
            # Reglas para estado de la planta
            ctrl.Rule(
                (self.temperature['óptima'] & self.humidity['óptima'] & 
                 self.soil['húmedo'] & self.light['óptima']),
                self.plant_state['bueno']
            ),
            ctrl.Rule(
                (self.temperature['óptima'] & self.humidity['óptima'] & 
                 self.soil['húmedo']),
                self.plant_state['bueno']
            ),
            ctrl.Rule(
                (self.temperature['fría'] | self.temperature['caliente'] | 
                 self.humidity['baja'] | self.humidity['alta'] | 
                 self.soil['seco'] | self.soil['empapado'] | 
                 self.light['baja'] | self.light['alta']),
                self.plant_state['malo']
            ),
            ctrl.Rule(
                (self.temperature['óptima'] | self.humidity['óptima'] | 
                 self.soil['húmedo'] | self.light['óptima']),
                self.plant_state['regular']
            ),

            # Reglas para tiempo de bomba
            ctrl.Rule(
                (self.soil['seco'] & self.humidity['baja']),
                self.pump_time['largo']
            ),
            ctrl.Rule(
                (self.soil['seco'] | self.humidity['baja']),
                self.pump_time['medio']
            ),
            ctrl.Rule(
                (self.soil['húmedo'] & self.humidity['óptima']),
                self.pump_time['corto']
            ),
            ctrl.Rule(
                (self.soil['empapado'] | self.humidity['alta']),
                self.pump_time['corto']
            )
        ]

        # Crear sistema de control
        self.plant_ctrl = ctrl.ControlSystem(self.rules)
        self.plant_sim = ctrl.ControlSystemSimulation(self.plant_ctrl)

    def evaluate_conditions(self, temperatura, humedad, suelo, luz):
        """
        Evalúa las condiciones actuales usando lógica difusa
        """
        try:
            # Establecer valores de entrada
            self.plant_sim.input['temperatura'] = float(temperatura)
            self.plant_sim.input['humedad'] = float(humedad)
            self.plant_sim.input['suelo'] = float(suelo)
            self.plant_sim.input['luz'] = float(luz)

            # Calcular resultado
            self.plant_sim.compute()

            # Obtener estado y tiempo de bomba
            estado = float(self.plant_sim.output['estado_planta'])
            tiempo_bomba = float(self.plant_sim.output['tiempo_bomba'])

            # Determinar si se debe activar la bomba
            should_activate = tiempo_bomba > 2  # Solo activar si el tiempo es mayor a 2 segundos

            return {
                "estado": round(estado, 2),
                "activar_bomba": should_activate,
                "tiempo_bomba": round(tiempo_bomba, 2),
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
                "activar_bomba": False,
                "tiempo_bomba": 0,
                "condiciones": {
                    "temperatura": float(temperatura),
                    "humedad": float(humedad),
                    "suelo": float(suelo),
                    "luz": float(luz)
                }
            } 