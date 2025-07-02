# La Spaziale S50 Coffee Machine Controller

A Python interface for controlling La Spaziale S50-QSS Robot coffee machines via Modbus RTU protocol.

## Overview

This project provides a Python class for interacting with La Spaziale S50 coffee machines equipped with the QSS Robot interface. It allows for:

- Reading machine information (serial number, firmware version)
- Monitoring machine status (group selection, sensor faults, purge countdown)
- Sending coffee delivery commands (various coffee types)
- Controlling water and MAT delivery

## Requirements

- Python 3.6+
- pymodbus 3.9.2+
- pyserial 3.5+

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/la-spaziale-s50.git
   cd la-spaziale-s50
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

```python
from test_communction import LaSpazialeCoffeeMachine

# Initialize coffee machine (adjust port as needed)
coffee_machine = LaSpazialeCoffeeMachine(port='COM4')  # Windows
# coffee_machine = LaSpazialeCoffeeMachine(port='/dev/ttyUSB0')  # Linux

# Connect to the machine
if coffee_machine.connect():
    try:
        # Read machine information
        serial = coffee_machine.get_serial_number()
        firmware = coffee_machine.get_firmware_version()
        print(f"Connected to machine: {serial}, firmware: {firmware}")
        
        # Deliver a single medium coffee from group 1
        coffee_machine.deliver_single_medium(1)
        
        # Wait for coffee delivery to complete
        import time
        time.sleep(5)
        
        # Check status
        status = coffee_machine.get_group_selection(1)
        print(f"Group 1 status: {status}")
        
    finally:
        # Always disconnect when done
        coffee_machine.disconnect()
```

## Available Commands

### Machine Information
- `get_serial_number()` - Read board serial number
- `get_firmware_version()` - Read firmware version
- `get_number_of_groups()` - Get total number of groups present
- `is_machine_blocked()` - Check if coffee machine is blocked

### Group Status
- `get_group_selection(group_num)` - Get current selection/delivery status for a group
- `get_sensor_fault(group_num)` - Check if volumetric sensor has fault
- `get_purge_countdown(group_num)` - Get seconds until automatic purge

### Coffee Commands
- `deliver_single_short(group_num)` - Deliver single short coffee
- `deliver_single_medium(group_num)` - Deliver single medium coffee
- `deliver_single_long(group_num)` - Deliver single long coffee
- `deliver_double_short(group_num)` - Deliver double short coffee
- `deliver_double_medium(group_num)` - Deliver double medium coffee
- `deliver_double_long(group_num)` - Deliver double long coffee
- `stop_delivery(group_num)` - Stop ongoing delivery
- `start_purge(group_num)` - Start purge cycle

### Other Commands
- `send_water_command(set_num)` - Send water delivery command
- `send_mat_command(set_num)` - Send MAT delivery command

## Protocol Documentation

This implementation is based on the QSS Robot Modbus Registers and Protocol documentation. The coffee machine communicates using Modbus RTU protocol with the following settings:
- Baudrate: 9600 bps
- Data bits: 8
- Parity: None
- Stop bits: 1

## Future Improvements

- Add logging functionality
- Add command line arguments for easier usage
- Improve error handling with try-catch blocks
- Add more comprehensive documentation

## License

QSS Robot License

## Author

Ammar Alsamani