import numpy as np
import matplotlib.pyplot as plt
from fuzzy_service import FuzzyService

def plot_fuzzy_sets():
    """
    Visualiza todos los conjuntos difusos del sistema
    """
    fuzzy_service = FuzzyService()
    
    # Crear figura con subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Temperatura
    ax1.plot(fuzzy_service.temp_range, fuzzy_service.temperature['fría'].mf, 'b', label='Fría')
    ax1.plot(fuzzy_service.temp_range, fuzzy_service.temperature['óptima'].mf, 'g', label='Óptima')
    ax1.plot(fuzzy_service.temp_range, fuzzy_service.temperature['caliente'].mf, 'r', label='Caliente')
    ax1.set_title('Conjuntos Difusos de Temperatura')
    ax1.set_xlabel('Temperatura (°C)')
    ax1.set_ylabel('Pertenencia')
    ax1.legend()
    ax1.grid(True)
    
    # Humedad
    ax2.plot(fuzzy_service.humidity_range, fuzzy_service.humidity['baja'].mf, 'b', label='Baja')
    ax2.plot(fuzzy_service.humidity_range, fuzzy_service.humidity['óptima'].mf, 'g', label='Óptima')
    ax2.plot(fuzzy_service.humidity_range, fuzzy_service.humidity['alta'].mf, 'r', label='Alta')
    ax2.set_title('Conjuntos Difusos de Humedad')
    ax2.set_xlabel('Humedad (%)')
    ax2.set_ylabel('Pertenencia')
    ax2.legend()
    ax2.grid(True)
    
    # Suelo
    ax3.plot(fuzzy_service.soil_range, fuzzy_service.soil['seco'].mf, 'b', label='Seco')
    ax3.plot(fuzzy_service.soil_range, fuzzy_service.soil['húmedo'].mf, 'g', label='Húmedo')
    ax3.plot(fuzzy_service.soil_range, fuzzy_service.soil['empapado'].mf, 'r', label='Empapado')
    ax3.set_title('Conjuntos Difusos de Humedad del Suelo')
    ax3.set_xlabel('Lectura del Sensor')
    ax3.set_ylabel('Pertenencia')
    ax3.legend()
    ax3.grid(True)
    
    # Luz
    ax4.plot(fuzzy_service.light_range, fuzzy_service.light['baja'].mf, 'b', label='Baja')
    ax4.plot(fuzzy_service.light_range, fuzzy_service.light['óptima'].mf, 'g', label='Óptima')
    ax4.plot(fuzzy_service.light_range, fuzzy_service.light['alta'].mf, 'r', label='Alta')
    ax4.set_title('Conjuntos Difusos de Luz')
    ax4.set_xlabel('Lectura del Sensor')
    ax4.set_ylabel('Pertenencia')
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig('fuzzy_sets.png')
    plt.close()

def plot_output_sets():
    """
    Visualiza los conjuntos difusos de salida
    """
    fuzzy_service = FuzzyService()
    
    # Crear figura con subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Estado de la Planta
    plant_range = np.arange(0, 100, 1)
    ax1.plot(plant_range, fuzzy_service.plant_state['malo'].mf, 'r', label='Malo')
    ax1.plot(plant_range, fuzzy_service.plant_state['regular'].mf, 'y', label='Regular')
    ax1.plot(plant_range, fuzzy_service.plant_state['bueno'].mf, 'g', label='Bueno')
    ax1.set_title('Conjuntos Difusos del Estado de la Planta')
    ax1.set_xlabel('Estado (0-100)')
    ax1.set_ylabel('Pertenencia')
    ax1.legend()
    ax1.grid(True)
    
    # Tiempo de Bomba
    pump_range = np.arange(0, 60, 1)
    ax2.plot(pump_range, fuzzy_service.pump_time['corto'].mf, 'g', label='Corto')
    ax2.plot(pump_range, fuzzy_service.pump_time['medio'].mf, 'y', label='Medio')
    ax2.plot(pump_range, fuzzy_service.pump_time['largo'].mf, 'r', label='Largo')
    ax2.set_title('Conjuntos Difusos del Tiempo de Bomba')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Pertenencia')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('fuzzy_outputs.png')
    plt.close()

def plot_surface_3d():
    """
    Visualiza superficies 3D para algunas combinaciones importantes de variables
    """
    fuzzy_service = FuzzyService()
    
    # Crear figura con subplots
    fig = plt.figure(figsize=(15, 10))
    
    # Superficie 3D: Temperatura vs Humedad -> Estado de la Planta
    ax1 = fig.add_subplot(221, projection='3d')
    temp_range = np.arange(15, 40, 1)
    hum_range = np.arange(0, 100, 1)
    temp_mesh, hum_mesh = np.meshgrid(temp_range, hum_range)
    state_mesh = np.zeros_like(temp_mesh)
    
    for i in range(len(temp_range)):
        for j in range(len(hum_range)):
            fuzzy_service.plant_sim.input['temperatura'] = temp_range[i]
            fuzzy_service.plant_sim.input['humedad'] = hum_range[j]
            fuzzy_service.plant_sim.input['suelo'] = 600  # valor medio
            fuzzy_service.plant_sim.input['luz'] = 600    # valor medio
            fuzzy_service.plant_sim.compute()
            state_mesh[j, i] = fuzzy_service.plant_sim.output['estado_planta']
    
    ax1.plot_surface(temp_mesh, hum_mesh, state_mesh, cmap='viridis')
    ax1.set_title('Temperatura vs Humedad -> Estado')
    ax1.set_xlabel('Temperatura (°C)')
    ax1.set_ylabel('Humedad (%)')
    ax1.set_zlabel('Estado')
    
    # Superficie 3D: Suelo vs Humedad -> Tiempo de Bomba
    ax2 = fig.add_subplot(222, projection='3d')
    soil_range = np.arange(0, 1023, 50)
    hum_range = np.arange(0, 100, 5)
    soil_mesh, hum_mesh = np.meshgrid(soil_range, hum_range)
    pump_mesh = np.zeros_like(soil_mesh)
    
    for i in range(len(soil_range)):
        for j in range(len(hum_range)):
            fuzzy_service.plant_sim.input['temperatura'] = 25  # valor medio
            fuzzy_service.plant_sim.input['humedad'] = hum_range[j]
            fuzzy_service.plant_sim.input['suelo'] = soil_range[i]
            fuzzy_service.plant_sim.input['luz'] = 600    # valor medio
            fuzzy_service.plant_sim.compute()
            pump_mesh[j, i] = fuzzy_service.plant_sim.output['tiempo_bomba']
    
    ax2.plot_surface(soil_mesh, hum_mesh, pump_mesh, cmap='viridis')
    ax2.set_title('Suelo vs Humedad -> Tiempo Bomba')
    ax2.set_xlabel('Suelo')
    ax2.set_ylabel('Humedad (%)')
    ax2.set_zlabel('Tiempo (s)')
    
    plt.tight_layout()
    plt.savefig('fuzzy_surfaces.png')
    plt.close()

if __name__ == '__main__':
    plot_fuzzy_sets()
    plot_output_sets()
    plot_surface_3d()
    print("Gráficas generadas: fuzzy_sets.png, fuzzy_outputs.png, fuzzy_surfaces.png") 