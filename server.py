from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext

# Initialisation des données (coils, holding registers, etc.)
store = ModbusDeviceContext(
    di=ModbusSequentialDataBlock(0, [0]*100),    # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [0]*100),    # Coils
    hr=ModbusSequentialDataBlock(0, [13]*100),   # Holding Registers
    ir=ModbusSequentialDataBlock(0, [0]*100)     # Input Registers
)

# Contexte du serveur (1 slave par défaut, unit_id=1)
context = ModbusServerContext(devices = store, single=True)

# Démarrer le serveur sur le port 5020
StartTcpServer(context=context, address=("0.0.0.0", 502))
