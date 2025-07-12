#!/usr/bin/env python3
"""
Modbus Holding Register Writer

This script connects to a Modbus TCP device and writes a new value to a
specified holding register.

It performs the following steps:
1. Connects to the target device.
2. Reads the initial value of the specified holding register.
3. Writes the new value to the register.
4. Reads the register again to confirm the write was successful.
5. Prints the results of each step.

Usage:
    python3 modbus_writer.py --target <PLC_IP_ADDRESS> --slave <SLAVE_ID> --address <REGISTER_ADDRESS> --value <NEW_VALUE>

Example:
    python3 modbus_writer.py --target 192.168.1.10 --slave 1 --address 4 --value 150
"""

import argparse
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Default Modbus port for the SimplePLC
MODBUS_PORT = 502

def get_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="A Python script to write to a specific Modbus holding register.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--target", required=True, help="The IP address of the target PLC.")
    parser.add_argument("--slave", required=True, type=int, help="The Modbus slave ID to query.")
    parser.add_argument("--address", required=True, type=int, help="The address of the holding register to write to.")
    parser.add_argument("--value", required=True, type=int, help="The new integer value to write to the register.")
    return parser.parse_args()

def read_register(client, slave_id, address):
    """Reads a single holding register and returns its value."""
    try:
        response = client.read_holding_registers(address=address, count=1, slave=slave_id)
        if response.isError():
            print(f"  [!] Modbus Error on read: {response}")
            return None
        if not response.registers:
            print("  [!] No data received in read response.")
            return None
        return response.registers[0]
    except ModbusException as e:
        print(f"  [!] Pymodbus Exception on read: {e}")
        return None

def write_register(client, slave_id, address, value):
    """Writes a value to a single holding register."""
    try:
        response = client.write_register(address=address, value=value, slave=slave_id)
        if response.isError():
            print(f"  [!] Modbus Error on write: {response}")
            return False
        return True
    except ModbusException as e:
        print(f"  [!] Pymodbus Exception on write: {e}")
        return False

def main():
    """Main execution function."""
    args = get_args()

    print(f"[~] Attempting to connect to {args.target}:{MODBUS_PORT}...")
    client = ModbusTcpClient(args.target, port=MODBUS_PORT)

    try:
        if not client.connect():
            print(f"[!] Connection to {args.target} failed. Please check the IP address and network.")
            return

        print(f"[+] Successfully connected to {args.target}.")
        print("-" * 60)

        # 1. Read the original value
        print(f"[~] Reading original value from holding register {args.address}...")
        original_value = read_register(client, args.slave, args.address)

        if original_value is None:
            print("[!] Failed to read the original value. Aborting write operation.")
            return

        print(f"  [+] Original value: {original_value}")
        print("-" * 60)

        # 2. Write the new value
        print(f"[~] Writing new value ({args.value}) to holding register {args.address}...")
        write_success = write_register(client, args.slave, args.address, args.value)

        if not write_success:
            print("[!] Write operation failed. The register was not changed.")
            return

        print("  [+] Write command sent successfully.")
        print("-" * 60)

        # 3. Read the value again to confirm
        print(f"[~] Reading value again to confirm the change...")
        new_value = read_register(client, args.slave, args.address)

        if new_value is None:
            print("[!] Failed to read the value after writing.")
            return

        print(f"  [+] New value: {new_value}")
        print("-" * 60)

        # 4. Final confirmation
        if new_value == args.value:
            print(f"[OK] Success! Register {args.address} was changed from {original_value} to {new_value}.")
        else:
            print(f"[!] Verification failed! Wrote {args.value}, but read back {new_value}.")

    finally:
        if client.is_socket_open():
            client.close()
            print("\n[~] Connection closed.")

if __name__ == "__main__":
    main()
