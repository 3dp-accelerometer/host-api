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
    SET_OUTPUT_DATA_RATE = 1
    GET_OUTPUT_DATA_RATE = 2
    SET_RANGE = 3
    GET_RANGE = 4
    SET_SCALE = 5
    GET_SCALE = 6
    DEVICE_REBOOT = 32
    SAMPLING_START = 33
    SAMPLING_START_N = 34
    SAMPLING_STOP = 35
