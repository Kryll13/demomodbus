"""Serveur Modbus TCP avec simulation de température.

Carte mémoire (CO : Coils, DI : Discrete Inputs, HR : Holding Registers, IR : Input Registers) :
    CO 0        : chauffage (écrit par new_client_on.py / new_client_off.py)
    DI 0 / 1    : température > 25 °C / température < 15 °C
    HR 0        : registre de maintien inutilisé
    IR 0        : température en °C, FLOAT32 (2 registres)
"""

import asyncio
import random

from pymodbus.client import ModbusTcpClient
from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

DEVICE_ID = 1
ADDRESS = ("0.0.0.0", 502)

READ_COILS = 1
READ_DISCRETE_INPUTS = 2
READ_INPUT_REGISTERS = 4

CO_HEATING = 0
DI_HIGH_TEMP = 0
DI_LOW_TEMP = 1
IR_TEMPERATURE = 0

TEMP_START = 20.0
TEMP_MIN = 10.0
TEMP_MAX = 30.0
TEMP_HIGH = 25.0
TEMP_LOW = 15.0


def to_registers(temperature: float) -> list[int]:
    """Convertit une température en 2 registres FLOAT32."""
    return ModbusTcpClient.convert_to_registers(
        temperature, ModbusTcpClient.DATATYPE.FLOAT32
    )


def build_device() -> SimDevice:
    """Décrit les 4 blocs de données du serveur."""
    return SimDevice(
        id=DEVICE_ID,
        simdata=(
            [SimData(CO_HEATING, values=False, datatype=DataType.BITS)],
            [
                SimData(DI_HIGH_TEMP, values=False, datatype=DataType.BITS),
                SimData(DI_LOW_TEMP, values=False, datatype=DataType.BITS),
            ],
            [SimData(0, values=0, datatype=DataType.REGISTERS)],
            [SimData(IR_TEMPERATURE, values=TEMP_START, datatype=DataType.FLOAT32)],
        ),
    )


async def temperature_simulation(server: ModbusTcpServer) -> None:
    """Fait varier la température selon l'état du chauffage."""
    temperature = TEMP_START

    while True:
        heating_on = (
            await server.async_getValues(DEVICE_ID, READ_COILS, CO_HEATING, count=1)
        )[0]

        temperature += (
            random.uniform(0.1, 0.5) if heating_on else -random.uniform(0.1, 0.3)
        )
        temperature = min(max(temperature, TEMP_MIN), TEMP_MAX)

        await server.async_setValues(
            DEVICE_ID, READ_INPUT_REGISTERS, IR_TEMPERATURE, to_registers(temperature)
        )
        await server.async_setValues(
            DEVICE_ID, READ_DISCRETE_INPUTS, DI_HIGH_TEMP, [temperature > TEMP_HIGH]
        )
        await server.async_setValues(
            DEVICE_ID, READ_DISCRETE_INPUTS, DI_LOW_TEMP, [temperature < TEMP_LOW]
        )

        print(f"T = {temperature:.1f} °C | Chauffage = {'ON' if heating_on else 'OFF'}")
        await asyncio.sleep(1)


async def main() -> None:
    server = ModbusTcpServer(build_device(), address=ADDRESS)
    await server.serve_forever(background=True)

    print("Serveur Modbus TCP démarré sur le port 502...")
    await temperature_simulation(server)


if __name__ == "__main__":
    asyncio.run(main())
