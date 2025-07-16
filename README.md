# Modbus TCP Tool

A comprehensive Python script for interacting with Modbus TCP devices via the command line. This utility supports reading and writing both coils and holding registers.

## Features

- Read a range of coils
- Write to a single coil
- Read a range of holding registers
- Write to a single holding register
- Modular design with verbose logging support

## Requirements

- Python 3.x
- `pymodbus` library

Install dependencies with:

```bash
pip install pymodbus
```

## Usage

```bash
python3 modbus-enum.py <command> [options]
```

### Commands

#### Read Coils

```bash
python3 modbus-enum.py read-coils --target <IP> --slave <ID> --start <START> --end <END>
```

#### Write Coil

```bash
python3 modbus-enum.py write-coil --target <IP> --slave <ID> --address <ADDR> --value <0|1>
```

#### Read Holding Registers

```bash
python3 modbus-enum.py read-registers --target <IP> --slave <ID> --start <START> --end <END>
```

#### Write Holding Register

```bash
python3 modbus-enum.py write-register --target <IP> --slave <ID> --address <ADDR> --value <INT>
```

Use `--verbose` with any command for debug logging.

## Example

```bash
python3 modbus-enum.py read-coils --target 192.168.1.100 --slave 1 --start 0 --end 10 --verbose
```
