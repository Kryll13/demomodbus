"""Serveur Modbus TCP : chauffage et température dans un registre de maintien.

Carte mémoire (CO : Coils, DI : Discrete Inputs, HR : Holding Registers, IR : Input Registers) :
    CO 0        : chauffage, actif au démarrage
    DI 0        : capteur inutilisé
    HR 0        : température en °C, FLOAT32 (2 registres)
    IR 0        : registre d'entrée inutilisé
"""

import asyncio
import random

from pymodbus.client import ModbusTcpClient
from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

DEVICE_ID = 1
ADDRESS = ("0.0.0.0", 502)

READ_COILS = 1
READ_HOLDING_REGISTERS = 3

CO_HEATING = 0
HR_TEMPERATURE = 0

TEMP_START = 20.0
TEMP_MAX = 30.0


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
            [SimData(CO_HEATING, values=True, datatype=DataType.BITS)],
            [SimData(0, values=False, datatype=DataType.BITS)],
            [SimData(HR_TEMPERATURE, values=TEMP_START, datatype=DataType.FLOAT32)],
            [SimData(0, values=0, datatype=DataType.REGISTERS)],
        ),
    )


async def temperature_simulation(server: ModbusTcpServer) -> None:
    """Fait monter la température tant que le chauffage est actif."""
    temperature = TEMP_START

    while True:
        heating_on = (
            await server.async_getValues(DEVICE_ID, READ_COILS, CO_HEATING, count=1)
        )[0]

        if heating_on:
            temperature = min(temperature + random.uniform(0.1, 0.5), TEMP_MAX)
            await server.async_setValues(
                DEVICE_ID,
                READ_HOLDING_REGISTERS,
                HR_TEMPERATURE,
                to_registers(temperature),
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
