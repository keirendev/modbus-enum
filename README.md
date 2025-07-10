# Modbus Holding Register Reader

## Overview

This is a simple, educational command-line tool designed to read a specific range of Holding Registers from a Modbus TCP device. Its primary purpose is to provide a clear and heavily commented example of how to connect to a Modbus device and read data using the `pymodbus` library in Python.

## Features

-   Connects to any Modbus TCP device over the network.
-   Reads a user-specified range of holding registers (Function Code 0x03).
-   Prints the values of the read registers to the console.
-   Includes a verbose mode for detailed debugging output.

Install pymodbus
```
pip install pymodbus
```

Usage
The script is run from the command line and requires a target IP address, a starting register address, and an ending register address.

```
python3 read-hr.py --target <IP_ADDRESS> --start <START_ADDRESS> --end <END_ADDRESS> [--verbose]
```

Command-Line Arguments
```
--target: (Required) The IP address of the Modbus TCP device you want to connect to.

--start: (Required) The first holding register address in the range you want to read.

--end: (Required) The last holding register address in the inclusive range you want to read.

--verbose: (Optional) An optional flag that, when included, enables detailed debug logging. This is useful for troubleshooting connection issues or viewing the raw Modbus traffic.
```

Example
To read holding registers from address 100 to 110 on a device with the IP address 192.168.1.52, you would use the following command:

```
python3 read-hr.py --target 192.168.1.52 --start 100 --end 110
```

To run the same command with detailed debugging output:

```
python3 read-hr.py --target 192.168.1.52 --start 100 --end 110 --verbose
```