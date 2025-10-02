from pymodbus.client import ModbusTcpClient

# Connexion au serveur Modbus
client = ModbusTcpClient('127.0.0.1', port=502)
client.connect()

client.write_coil(address=0, value=False)

client.close()