from threading import Thread
import time
import random
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext

SLAVE_ID = 0

STORE_CO = 1
CO_HEATING = 0

STORE_DI = 2
DI_HIGH_TEMP = 0
DI_LOW_TEMP = 1

STORE_IR = 4
IR_TEMPERATURE = 0

# -------- Simulation de la température --------
def temperature_simulation(context, slave_id=SLAVE_ID):
    temperature = 20.0
    heating_on = False
    while True:
        # Lire l'état du chauffage
        heating_on = bool(context[slave_id].getValues(STORE_CO, CO_HEATING, count=1)[0])  # Coil 0

        # Faire varier la température
        if heating_on:
            temperature += random.uniform(0.1, 0.5)
        else:
            temperature -= random.uniform(0.1, 0.3)

        # bornes
        if temperature < 10:
            temperature = 10
        if temperature > 30:
            temperature = 30

        # Écrire dans registre (Input Register 0, valeur entière)
        context[slave_id].setValues(STORE_IR, IR_TEMPERATURE, [int(temperature * 10)])  # *10 pour précision

        # Capteurs discrets
        high_temp = 1 if temperature > 25 else 0
        low_temp = 1 if temperature < 15 else 0

        context[slave_id].setValues(STORE_DI, DI_HIGH_TEMP, [high_temp])  # DI0
        context[slave_id].setValues(STORE_DI, DI_LOW_TEMP, [low_temp])   # DI1

        # Affichage console
        print(f"T = {temperature:.1f} °C | Chauffage={'ON' if heating_on else 'OFF'} | >25={high_temp} | <15={low_temp}")

        time.sleep(1)



if __name__ == "__main__":
    # -------- Configuration initiale --------
    # Coil 0 = bouton chauffage (ON/OFF)
    # Discrete Inputs:
    #   DI 0 = capteur > 25°C
    #   DI 1 = capteur < 15°C
    # Input Register 0 = température courante (°C * 10 pour garder 1 décimale si besoin)

    store = ModbusDeviceContext(
        di=ModbusSequentialDataBlock(SLAVE_ID, [0] * 10),
        co=ModbusSequentialDataBlock(SLAVE_ID, [0] * 10),
        hr=ModbusSequentialDataBlock(SLAVE_ID, [0] * 10),
        ir=ModbusSequentialDataBlock(SLAVE_ID, [0] * 10)
    )

    context = ModbusServerContext(devices=store, single=True)

    # Lancement du thread de simulation de température
    sim_thread = Thread(target=temperature_simulation, args=(context,))
    sim_thread.daemon = True
    sim_thread.start()

    # Démarrage du serveur Modbus TCP sur le port 502
    print("Serveur Modbus TCP démarré sur le port 502...")
    StartTcpServer(context, address=("0.0.0.0", 502))