import random
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from threading import Thread

# Adresse du registre où la température sera stockée
TEMPERATURE_REGISTER = 0
STATUS_COIL = 0

def temperature_simulation(context, slave_id=0x00):
    """Simule une variation de température toutes les secondes."""
    temperature = 200  # Température initiale (ex: 20.0°C, multipliée par 10)
    while True:
        status = context[slave_id].getValues(1, STATUS_COIL)[0]
        if status:  # Si le chauffage est en marche
            # Variation aléatoire de la température
            temperature += random.randint(-2, 2)
            if temperature < 200:
                temperature = 200
            if temperature > 300:
                temperature = 300
            # Mise à jour du registre
            context[slave_id].setValues(3, TEMPERATURE_REGISTER, [temperature])

        time.sleep(1)

if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 10 mots
    device = ModbusDeviceContext(
        co=ModbusSequentialDataBlock(0, [True]*10),    # en marche initialement
        hr=ModbusSequentialDataBlock(0, [200]*10)  # 20.0°C initial
    )
    context = ModbusServerContext(devices=device, single=True)

    # Lancement du thread de simulation de température
    sim_thread = Thread(target=temperature_simulation, args=(context,))
    sim_thread.daemon = True
    sim_thread.start()

    # Démarrage du serveur Modbus TCP sur le port 502
    print("Serveur Modbus TCP démarré sur le port 502...")
    StartTcpServer(context, address=("0.0.0.0", 502))