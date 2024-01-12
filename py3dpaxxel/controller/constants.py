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


OutputDataRateFromHz = {
    3200: OutputDataRate.ODR3200,
    1600: OutputDataRate.ODR1600,
    800: OutputDataRate.ODR800,
    400: OutputDataRate.ODR400,
    200: OutputDataRate.ODR200,
    100: OutputDataRate.ODR100,
    50: OutputDataRate.ODR50,
    25: OutputDataRate.ODR25,
    12.5: OutputDataRate.ODR12_5,
    6.25: OutputDataRate.ODR6_25,
    3.13: OutputDataRate.ODR3_13,
    1.56: OutputDataRate.ODR1_56,
    0.78: OutputDataRate.ODR0_78,
    0.39: OutputDataRate.ODR0_39,
    0.20: OutputDataRate.ODR0_20,
    0.10: OutputDataRate.ODR0_10
}

OutputDataRateDelay = {
    OutputDataRate.ODR3200: 1.0 / 3200,
    OutputDataRate.ODR1600: 1.0 / 1600,
    OutputDataRate.ODR800: 1.0 / 800,
    OutputDataRate.ODR400: 1.0 / 400,
    OutputDataRate.ODR200: 1.0 / 200,
    OutputDataRate.ODR100: 1.0 / 100,
    OutputDataRate.ODR50: 1.0 / 50,
    OutputDataRate.ODR25: 1.0 / 25,
    OutputDataRate.ODR12_5: 1.0 / 12.5,
    OutputDataRate.ODR6_25: 1.0 / 6.25,
    OutputDataRate.ODR3_13: 1.0 / 3.13,
    OutputDataRate.ODR1_56: 1.0 / 1.56,
    OutputDataRate.ODR0_78: 1.0 / 0.78,
    OutputDataRate.ODR0_39: 1.0 / 0.39,
    OutputDataRate.ODR0_20: 1.0 / 0.20,
    OutputDataRate.ODR0_10: 1.0 / 0.10,
}


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
    TX_SET_OUTPUT_DATA_RATE = 1
    TX_GET_OUTPUT_DATA_RATE = 2
    TX_SET_RANGE = 3
    TX_GET_RANGE = 4
    TX_SET_SCALE = 5
    TX_GET_SCALE = 6
    TX_GET_DEVICE_SETUP = 7
    TX_GET_FIRMWARE_VERSION = 8
    TX_GET_UPTIME = 9

    # sampling (tx)
    TX_DEVICE_REBOOT = 17
    TX_SAMPLING_START = 18
    TX_SAMPLING_STOP = 19

    # configuration (rx)
    RX_OUTPUT_DATA_RATE = 25
    RX_RANGE = 26
    RX_SCALE = 27
    RX_DEVICE_SETUP = 28
    RX_FIRMWARE_VERSION = 29
    RX_UPTIME = 30

    # sampling (rx)
    RX_SAMPLING_FIFO_OVERFLOW = 33
    RX_SAMPLING_STARTED = 34
    RX_SAMPLING_FINISHED = 35
    RX_SAMPLING_STOPPED = 36
    RX_SAMPLING_ABORTED = 37
    RX_ACCELERATION = 38
    RX_ERROR = 39


class ErrorCode(Enum):
    UNDEFINED = 0
    USB_ERROR = 1
    USAGE_FAULT_HANDLER = 2
    BUS_FAULT_HANDLER = 3
    HARD_FAULT_HANDLER = 4
    ERROR_HANDLER = 5
