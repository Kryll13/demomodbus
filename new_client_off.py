"""Client Modbus TCP : éteint le chauffage (CO 0)."""

from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("127.0.0.1", port=502)
client.connect()

client.write_coil(address=0, value=False)

client.close()
