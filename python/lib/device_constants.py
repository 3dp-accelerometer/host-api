from enum import Enum


class OutputDataRate(Enum):
    ODR3200 = 0b1111
    ODR1600 = 0b1110
    ODR800 = 0b1101
    ODR400 = 0b1100
    ODR200 = 0b1011
    ODR100 = 0b1010
    ODR50 = 0b1001
    ODR25 = 0b1000
    ODR12_5 = 0b0111
    ODR6_25 = 0b0110
    ODR3_13 = 0b0101
    ODR1_56 = 0b0100
    ODR0_78 = 0b0011
    ODR0_39 = 0b0010
    ODR0_20 = 0b0001
    ODR0_10 = 0b0000


class Range(Enum):
    G2 = 0b00
    G4 = 0b01
    G8 = 0b10
    G16 = 0b11


class Scale(Enum):
    FULL_RES_4MG_LSB = 1
    SCALED_10BIT = 0


class TransportHeaderId(Enum):
    # configuration (tx)
    SET_OUTPUT_DATA_RATE = 1
    GET_OUTPUT_DATA_RATE = 2
    SET_RANGE = 3
    GET_RANGE = 4
    SET_SCALE = 5
    GET_SCALE = 6
    # sampling (tx)
    DEVICE_REBOOT = 16
    SAMPLING_START = 17
    SAMPLING_STOP = 18
    # responses (rx)
    SAMPLING_FIFO_OVERFLOW = 24
    SAMPLING_STARTED = 25
    SAMPLING_FINISHED = 26
    SAMPLING_STOPPED = 27
    SAMPLING_ABORTED = 28
    ACCELERATION = 29
