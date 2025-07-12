#!/usr/bin/env python3
"""
Modbus Coil Writer

This script connects to a Modbus TCP device and writes a new value (ON/OFF)
to a specified Coil. Coils are the readable and writable digital outputs of a PLC.
Note: Discrete Inputs are read-only and cannot be written to.

It performs the following steps:
1. Connects to the target device.
2. Reads the initial state of the specified Coil.
3. Writes the new state to the Coil.
4. Reads the Coil again to confirm the write was successful.
5. Prints the results of each step.

Usage:
    python3 modbus_coil_writer.py --target <PLC_IP_ADDRESS> --slave <SLAVE_ID> --address <COIL_ADDRESS> --value <0_for_OFF_or_1_for_ON>

Example:
    python3 modbus_coil_writer.py --target 192.168.1.10 --slave 1 --address 15 --value 1
"""

import argparse
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Default Modbus port for the SimplePLC
MODBUS_PORT = 502

def get_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="A Python script to write to a specific Modbus Coil.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--target", required=True, help="The IP address of the target PLC.")
    parser.add_argument("--slave", required=True, type=int, help="The Modbus slave ID to query.")
    parser.add_argument("--address", required=True, type=int, help="The address of the Coil to write to.")
    parser.add_argument("--value", required=True, type=int, choices=[0, 1], help="The new state for the coil (0 for OFF, 1 for ON).")
    return parser.parse_args()

def read_coil(client, slave_id, address):
    """Reads a single coil and returns its boolean state."""
    try:
        response = client.read_coils(address=address, count=1, slave=slave_id)
        if response.isError():
            print(f"  [!] Modbus Error on read: {response}")
            return None
        if not hasattr(response, 'bits') or not response.bits:
            print("  [!] No data received in read response.")
            return None
        return response.bits[0]
    except ModbusException as e:
        print(f"  [!] Pymodbus Exception on read: {e}")
        return None

def write_coil(client, slave_id, address, value):
    """Writes a boolean value to a single coil."""
    try:
        # The value for write_coil must be a boolean (True/False)
        response = client.write_coil(address=address, value=bool(value), slave=slave_id)
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
    new_state_bool = bool(args.value)

    print(f"[~] Attempting to connect to {args.target}:{MODBUS_PORT}...")
    client = ModbusTcpClient(args.target, port=MODBUS_PORT)

    try:
        if not client.connect():
            print(f"[!] Connection to {args.target} failed. Please check the IP address and network.")
            return

        print(f"[+] Successfully connected to {args.target}.")
        print("-" * 60)

        # 1. Read the original state
        print(f"[~] Reading original state from Coil {args.address}...")
        original_state = read_coil(client, args.slave, args.address)

        if original_state is None:
            print("[!] Failed to read the original state. Aborting write operation.")
            return

        print(f"  [+] Original state: {'ON' if original_state else 'OFF'} ({original_state})")
        print("-" * 60)

        # 2. Write the new state
        print(f"[~] Writing new state ({'ON' if new_state_bool else 'OFF'}) to Coil {args.address}...")
        write_success = write_coil(client, args.slave, args.address, new_state_bool)

        if not write_success:
            print("[!] Write operation failed. The Coil was not changed.")
            return

        print("  [+] Write command sent successfully.")
        print("-" * 60)

        # 3. Read the state again to confirm
        print(f"[~] Reading state again to confirm the change...")
        new_state = read_coil(client, args.slave, args.address)

        if new_state is None:
            print("[!] Failed to read the state after writing.")
            return

        print(f"  [+] New state: {'ON' if new_state else 'OFF'} ({new_state})")
        print("-" * 60)

        # 4. Final confirmation
        if new_state == new_state_bool:
            print(f"[OK] Success! Coil {args.address} was changed from {'ON' if original_state else 'OFF'} to {'ON' if new_state else 'OFF'}.")
        else:
            print(f"[!] Verification failed! Wrote {new_state_bool}, but read back {new_state}.")

    finally:
        if client.is_socket_open():
            client.close()
            print("\n[~] Connection closed.")

if __name__ == "__main__":
    main()
