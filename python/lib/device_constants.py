from enum import Enum


class OutputDataRate(Enum):
    ODR3200 = 0b1111
    ODR1600 = 0b1110
    ODR800 = 0b1101
    ODR400 = 0b1100
    ODR200 = 0b1011
    ODR100 = 0b1010
    ODR50 = 0b1001


class Range(Enum):
    G2 = 0b00
    G4 = 0b01
    G8 = 0b10
    G16 = 0b11


class Scale(Enum):
    FULL_RES_G4 = 0
    SCALED_10BIT = 1


class TransportHeaderId(Enum):
    SetOutputDataRate = 1
    GetOutputDataRate = 2
    SetRange = 3
    GetRange = 4
    SetScale = 5
    GetScale = 6
