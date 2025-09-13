from pymodbus.client import ModbusTcpClient

# Connexion au serveur Modbus
client = ModbusTcpClient('127.0.0.1', port=502)
client.connect()

# Lecture de registres
result = client.read_holding_registers(address=0)
if not result.isError():
    print("Valeurs des registres:", result.registers)

# Écriture dans un registre
client.write_register(address=0, value=17)

client.close()