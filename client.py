"""Client Modbus TCP minimal : lecture de HR 0, écriture de CO 0."""

from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("127.0.0.1", port=502)
client.connect()

result = client.read_holding_registers(address=0)
if not result.isError():
    print("Valeur de HR 0 :", result.registers)

client.write_coil(address=0, value=True)

client.close()
