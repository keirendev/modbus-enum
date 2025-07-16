#!/usr/bin/env python3
"""
A comprehensive Modbus TCP tool for reading and writing coils and holding registers.

This script provides a command-line interface to interact with Modbus TCP devices,
allowing users to perform the following actions:
- Read a range of coils
- Write to a single coil
- Read a range of holding registers
- Write to a single holding register

The tool is designed with a clear, modular structure and robust error handling
to ensure reliability and ease of use in a production environment.

Usage:
    python3 modbus_tool.py <command> [options]

Commands:
    read-coils      Read a range of coils.
    write-coil      Write a single value to a coil.
    read-registers  Read a range of holding registers.
    write-register  Write a single value to a holding register.

Run `python3 modbus_tool.py <command> --help` for more information on a specific command.
"""

import argparse
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException, ConnectionException

# --- Global Configuration ---
MODBUS_PORT = 502

# --- Core Modbus Communication Functions ---

def read_coils(client, slave_id, start_address, count):
    """
    Reads a range of coils from the Modbus device.

    Args:
        client: An active ModbusTcpClient instance.
        slave_id (int): The slave ID to query.
        start_address (int): The starting address of the coils to read.
        count (int): The number of coils to read.

    Returns:
        list or None: A list of boolean values representing the coil states,
                      or None if an error occurred.
    """
    try:
        logging.info(f"Reading {count} coils starting from address {start_address}...")
        response = client.read_coils(address=start_address, count=count, slave=slave_id)
        if response.isError():
            logging.error(f"Modbus error on read: {response}")
            return None
        return response.bits[:count]
    except ModbusException as e:
        logging.error(f"Pymodbus exception on read: {e}")
        return None

def write_coil(client, slave_id, address, value):
    """
    Writes a single value to a coil on the Modbus device.

    Args:
        client: An active ModbusTcpClient instance.
        slave_id (int): The slave ID to query.
        address (int): The address of the coil to write to.
        value (bool): The boolean value to write (True for ON, False for OFF).

    Returns:
        bool: True if the write was successful, False otherwise.
    """
    try:
        logging.info(f"Writing {'ON' if value else 'OFF'} to coil {address}...")
        response = client.write_coil(address=address, value=value, slave=slave_id)
        if response.isError():
            logging.error(f"Modbus error on write: {response}")
            return False
        return True
    except ModbusException as e:
        logging.error(f"Pymodbus exception on write: {e}")
        return False

def read_holding_registers(client, slave_id, start_address, count):
    """
    Reads a range of holding registers from the Modbus device.

    Args:
        client: An active ModbusTcpClient instance.
        slave_id (int): The slave ID to query.
        start_address (int): The starting address of the registers to read.
        count (int): The number of registers to read.

    Returns:
        list or None: A list of integer values from the registers,
                      or None if an error occurred.
    """
    try:
        logging.info(f"Reading {count} holding registers starting from address {start_address}...")
        response = client.read_holding_registers(address=start_address, count=count, slave=slave_id)
        if response.isError():
            logging.error(f"Modbus error on read: {response}")
            return None
        return response.registers
    except ModbusException as e:
        logging.error(f"Pymodbus exception on read: {e}")
        return None

def write_holding_register(client, slave_id, address, value):
    """
    Writes a single value to a holding register on the Modbus device.

    Args:
        client: An active ModbusTcpClient instance.
        slave_id (int): The slave ID to query.
        address (int): The address of the register to write to.
        value (int): The integer value to write.

    Returns:
        bool: True if the write was successful, False otherwise.
    """
    try:
        logging.info(f"Writing value '{value}' to holding register {address}...")
        response = client.write_register(address=address, value=value, slave=slave_id)
        if response.isError():
            logging.error(f"Modbus error on write: {response}")
            return False
        return True
    except ModbusException as e:
        logging.error(f"Pymodbus exception on write: {e}")
        return False

# --- Command Handling Functions ---

def handle_read_coils(client, args):
    """Handler for the 'read-coils' command."""
    count = (args.end - args.start) + 1
    if count < 1:
        logging.error("End address must be greater than or equal to the start address.")
        return

    values = read_coils(client, args.slave, args.start, count)
    if values is not None:
        logging.info("Read successful! Displaying coil states:")
        for i, value in enumerate(values):
            current_address = args.start + i
            print(f"  Coil[{current_address}]: {'ON' if value else 'OFF'}")

def handle_write_coil(client, args):
    """Handler for the 'write-coil' command."""
    # 1. Read the original state
    original_state_list = read_coils(client, args.slave, args.address, 1)
    if original_state_list is None:
        logging.error("Failed to read the original coil state. Aborting write operation.")
        return
    original_state = original_state_list[0]
    logging.info(f"Original state of coil {args.address}: {'ON' if original_state else 'OFF'}")

    # 2. Write the new state
    new_state_bool = bool(args.value)
    if not write_coil(client, args.slave, args.address, new_state_bool):
        logging.error("Write operation failed. The coil was not changed.")
        return
    logging.info("Write command sent successfully.")

    # 3. Read back to confirm
    new_state_list = read_coils(client, args.slave, args.address, 1)
    if new_state_list is None:
        logging.error("Failed to read the coil state after writing.")
        return
    new_state = new_state_list[0]

    # 4. Final confirmation
    if new_state == new_state_bool:
        print(f"\n[SUCCESS] Coil {args.address} was changed from {'ON' if original_state else 'OFF'} to {'ON' if new_state else 'OFF'}.")
    else:
        print(f"\n[FAILURE] Verification failed! Wrote '{'ON' if new_state_bool else 'OFF'}', but read back '{'ON' if new_state else 'OFF'}.")

def handle_read_registers(client, args):
    """Handler for the 'read-registers' command."""
    count = (args.end - args.start) + 1
    if count < 1:
        logging.error("End address must be greater than or equal to the start address.")
        return

    values = read_holding_registers(client, args.slave, args.start, count)
    if values is not None:
        logging.info("Read successful! Displaying register values:")
        for i, value in enumerate(values):
            current_address = args.start + i
            print(f"  Register[{current_address}]: {value}")

def handle_write_register(client, args):
    """Handler for the 'write-register' command."""
    # 1. Read original value
    original_value_list = read_holding_registers(client, args.slave, args.address, 1)
    if original_value_list is None:
        logging.error("Failed to read the original register value. Aborting write operation.")
        return
    original_value = original_value_list[0]
    logging.info(f"Original value of register {args.address}: {original_value}")

    # 2. Write new value
    if not write_holding_register(client, args.slave, args.address, args.value):
        logging.error("Write operation failed. The register was not changed.")
        return
    logging.info("Write command sent successfully.")

    # 3. Read back to confirm
    new_value_list = read_holding_registers(client, args.slave, args.address, 1)
    if new_value_list is None:
        logging.error("Failed to read the register value after writing.")
        return
    new_value = new_value_list[0]

    # 4. Final confirmation
    if new_value == args.value:
        print(f"\n[SUCCESS] Register {args.address} was changed from {original_value} to {new_value}.")
    else:
        print(f"\n[FAILURE] Verification failed! Wrote {args.value}, but read back {new_value}.")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="A comprehensive Modbus TCP tool.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for debugging.")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Parent parser for common arguments ---
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--target", required=True, help="The IP address of the target Modbus device.")
    parent_parser.add_argument("--slave", required=True, type=int, help="The Modbus slave ID to query.")

    # --- Parser for 'read-coils' ---
    parser_read_coils = subparsers.add_parser("read-coils", parents=[parent_parser], help="Read a range of coils.")
    parser_read_coils.add_argument("--start", required=True, type=int, help="The starting coil address to read.")
    parser_read_coils.add_argument("--end", required=True, type=int, help="The ending coil address to read.")
    parser_read_coils.set_defaults(func=handle_read_coils)

    # --- Parser for 'write-coil' ---
    parser_write_coil = subparsers.add_parser("write-coil", parents=[parent_parser], help="Write to a single coil.")
    parser_write_coil.add_argument("--address", required=True, type=int, help="The address of the coil to write to.")
    parser_write_coil.add_argument("--value", required=True, type=int, choices=[0, 1], help="The new state for the coil (0 for OFF, 1 for ON).")
    parser_write_coil.set_defaults(func=handle_write_coil)

    # --- Parser for 'read-registers' ---
    parser_read_registers = subparsers.add_parser("read-registers", parents=[parent_parser], help="Read a range of holding registers.")
    parser_read_registers.add_argument("--start", required=True, type=int, help="The starting register address to read.")
    parser_read_registers.add_argument("--end", required=True, type=int, help="The ending register address to read.")
    parser_read_registers.set_defaults(func=handle_read_registers)

    # --- Parser for 'write-register' ---
    parser_write_register = subparsers.add_parser("write-register", parents=[parent_parser], help="Write to a single holding register.")
    parser_write_register.add_argument("--address", required=True, type=int, help="The address of the holding register to write to.")
    parser_write_register.add_argument("--value", required=True, type=int, help="The new integer value to write to the register.")
    parser_write_register.set_defaults(func=handle_write_register)

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Establish Modbus connection
    client = ModbusTcpClient(args.target, port=MODBUS_PORT)
    try:
        logging.info(f"Connecting to {args.target}:{MODBUS_PORT}...")
        if not client.connect():
            raise ConnectionException(f"Failed to connect to {args.target}")

        # Execute the function associated with the chosen command
        args.func(client, args)

    except ConnectionException as e:
        logging.error(f"Connection failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if client.is_socket_open():
            client.close()
            logging.info("Connection closed.")

if __name__ == "__main__":
    main()