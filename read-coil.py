#!/usr/bin/env python3
"""
A basic, educational script to read a specific range of Modbus Coils.

This tool focuses on doing one thing well: connecting to a Modbus TCP device
and reading a user-defined block of coils. The code is heavily
commented to explain the fundamental steps.
"""

# argparse is used to create the command-line interface. It lets us easily
# define arguments like --target, --start, and --end.
import argparse
# logging provides a better way to print messages than print(). It allows for
# different levels of severity (e.g., INFO for normal messages, ERROR for problems).
import logging

# We import the two main components we need from the pymodbus library:
# 1. ModbusTcpClient: The object that handles the network connection and communication.
# 2. ConnectionException: A specific error that occurs if the script can't connect.
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# --- Main Script Logic ---

# This is the standard Python entry point. The code inside this 'if' block
# will only run when you execute the script directly (e.g., `python3 basic_coil_reader.py`).
if __name__ == "__main__":

    # 1. SET UP COMMAND-LINE ARGUMENTS
    # ---------------------------------
    # We create a parser object to define what arguments our script accepts.
    parser = argparse.ArgumentParser(
        description="A basic tool to read a range of Modbus coils."
    )
    # --target: The IP address of the Modbus device. 'required=True' means the script won't run without it.
    parser.add_argument("--target", required=True, help="The IP address of the Modbus device.")
    # --start: The first coil address you want to read. We specify 'type=int' to convert the input to a number.
    parser.add_argument("--start", required=True, type=int, help="The starting coil address to read.")
    # --end: The last coil address you want to read.
    parser.add_argument("--end", required=True, type=int, help="The ending coil address to read.")
    # --verbose: An optional flag to show more detailed debug messages. 'action="store_true"' means it's a flag that doesn't take a value.
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for debugging.")

    # The parser reads the arguments from the command line (e.g., '172.19.9.3') and stores them in the 'args' object.
    args = parser.parse_args()

    # 2. CONFIGURE LOGGING
    # --------------------
    # This sets up our logging system. If --verbose is used, we see detailed DEBUG
    # messages. Otherwise, we only see informational (INFO) messages and above.
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    # 3. ESTABLISH THE MODBUS CONNECTION
    # ----------------------------------
    # We create an instance of the Modbus TCP client, passing it the target IP address.
    # The port defaults to 502, which is standard for Modbus TCP.
    client = ModbusTcpClient(args.target)
    
    # We wrap our main logic in a 'try...finally' block. This is very important!
    # The 'finally' block will ALWAYS run, even if an error occurs. This ensures
    # that we always close the network connection properly.
    try:
        logging.info(f"Connecting to {args.target}...")
        # This command attempts to open the network socket to the device.
        client.connect()

        # 4. READ THE COILS
        # -----------------
        # Coils (Function Code 0x01) are the simplest data type. They are single-bit
        # read/write memory locations, often representing a relay, a light, or a
        # digital on/off state (True/False).

        # Calculate how many coils we need to read in total.
        # We add 1 because the range is inclusive (e.g., reading 100 to 102 is 3 coils).
        address_to_read = args.start
        count_to_read = (args.end - args.start) + 1
        
        logging.info(f"Attempting to read {count_to_read} coils starting from address {address_to_read}...")

        # This is the core command to read coil data.
        # It takes the starting address and the number of coils to read.
        # The 'slave' or 'unit' ID is required for some devices, typically 1 for TCP.
        response = client.read_coils(address_to_read, count=count_to_read, slave=1)

        # 5. PROCESS THE RESPONSE
        # -----------------------
        # After sending the read request, we must check if it was successful.
        # The device might be busy, or the address might not exist.

        # The .isError() method is a simple way to check if the device returned an error.
        if response.isError():
            # If there was an error, we log it and exit.
            logging.error(f"Modbus Error: {response}")
        else:
            # If the read was successful, the data is stored in the '.bits' property.
            # This property is a list of booleans (True/False).
            logging.info("Read successful! Displaying coil states:")
            
            # We loop through the number of coils we requested.
            # The response.bits list might be longer than requested due to byte padding,
            # so we only loop through the number of coils we actually asked for.
            for i in range(count_to_read):
                # We calculate the actual coil address by adding the starting
                # address to the current index in the list.
                current_address = address_to_read + i
                
                # We must check if the index `i` is within the bounds of the returned bits list.
                if i < len(response.bits):
                    value = response.bits[i]
                    print(f"  Coil[{current_address}]: {value}")
                else:
                    # This case handles if the device returns fewer bits than requested,
                    # which can happen if the read request goes past the end of the valid addresses.
                    logging.warning(f"Device returned fewer coils than requested. Stopping at address {current_address - 1}.")
                    break

    # 6. HANDLE POTENTIAL ERRORS
    # --------------------------
    # This 'except' block will catch an error if the script fails to connect
    # to the IP address in the first place (e.g., wrong IP, device offline, firewall).
    except ConnectionException as e:
        logging.error(f"Connection failed: {e}")
    
    # This 'except' block catches any other general errors that might happen.
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    # 7. CLOSE THE CONNECTION
    # -----------------------
    # The 'finally' block ensures this code always runs.
    finally:
        # It's good practice to check if the socket is open before trying to close it.
        if client.is_socket_open():
            logging.info("Closing connection.")
            client.close()
