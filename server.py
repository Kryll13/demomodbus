"""Serveur Modbus TCP minimal.

Carte mémoire (CO : Coils, DI : Discrete Inputs, HR : Holding Registers, IR : Input Registers) :
    CO 0-99   : sortie booléenne
    DI 0-99   : entrée booléenne
    HR 0-99   : registre de maintien (valeur initiale 13)
    IR 0-99   : registre d'entrée
"""

from pymodbus.server import StartTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

store = SimDevice(
    id=1,
    simdata=(
        [SimData(0, count=100, values=False, datatype=DataType.BITS)],
        [SimData(0, count=100, values=False, datatype=DataType.BITS)],
        [SimData(0, count=100, values=13, datatype=DataType.REGISTERS)],
        [SimData(0, count=100, values=0, datatype=DataType.REGISTERS)],
    ),
)

StartTcpServer(context=store, address=("0.0.0.0", 502))
