import time
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

class LaSpazialeCoffeeMachine:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        """
        Initialize connection to LaSpaziale S50-QSS Robot
        
        Args:
            port: Serial port (e.g., 'COM4 or 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Communication speed (9600 bps as per spec)
        """
        self.client = ModbusSerialClient(
            # method='rtu',
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        self.node_address = 1  # 0x01 as per spec
        
    def connect(self):
        """Establish connection to the coffee machine"""
        return self.client.connect()
    
    def disconnect(self):
        """Close connection"""
        self.client.close()
    
    # Group 0: Identifying Functions
    def get_serial_number(self):
        """Read board serial number (20 chars)"""
        try:
            result = self.client.read_holding_registers(address=0, count=10)
            if result.isError():
                return None
            # Convert registers to string (each register = 2 chars)
            serial = ''.join([chr(reg >> 8) + chr(reg & 0xFF) for reg in result.registers])
            return serial.rstrip('\x00')  # Remove null terminators
        except Exception as e:
            print(f"Error reading serial number: {e}")
            return None
    
    def get_firmware_version(self):
        """Read firmware version"""
        try:
            result = self.client.read_holding_registers(address=11, count=1)
            if result.isError():
                return None
            reg = result.registers[0]
            major = (reg >> 8) & 0xFF
            minor = reg & 0xFF
            return f"{major}.{minor}"
        except Exception as e:
            print(f"Error reading firmware version: {e}")
            return None
    
    # Group 1: Coffee Machine State Functions
    def get_group_selection(self, group_num):
        """
        Get current selection/delivery status for a group (1-3)
        Returns dict with coffee types being delivered
        """
        if group_num < 1 or group_num > 3:
            raise ValueError("Group number must be 1-3")
        
        register_addr = 256 + (group_num - 1)  # Groups status starts at register 256 (HEX 0x100)
        
        try:
            result = self.client.read_holding_registers(register_addr, count=1)
            if result.isError():
                return None
            
            status = result.registers[0]
            return {
                'single_short': bool(status & 0x01),
                'single_long': bool(status & 0x02),
                'double_short': bool(status & 0x04),
                'double_long': bool(status & 0x08),
                'continuous_flow': bool(status & 0x10),
                'single_medium': bool(status & 0x20),
                'double_medium': bool(status & 0x40),
                'purge': bool(status & 0x80)
            }
        except Exception as e:
            print(f"Error reading group {group_num} selection: {e}")
            return None
    
    def get_sensor_fault(self, group_num):
        """Check if volumetric sensor has fault for group (1-3)"""
        if group_num < 1 or group_num > 3:
            raise ValueError("Group number must be 1-3")
        
        register_addr = 260 + (group_num - 1)  # Sensor faults start at 260
        
        try:
            result = self.client.read_holding_registers(register_addr, count=1)
            if result.isError():
                return None
            return result.registers[0] == 1
        except Exception as e:
            print(f"Error reading sensor fault for group {group_num}: {e}")
            return None
    
    def get_purge_countdown(self, group_num):
        """Get seconds until automatic purge for group (1-3)"""
        if group_num < 1 or group_num > 3:
            raise ValueError("Group number must be 1-3")
        
        register_addr = 264 + (group_num - 1)  # Purge countdown starts at 264
        
        try:
            result = self.client.read_holding_registers(register_addr, count=1)
            if result.isError():
                return None
            return result.registers[0]
        except Exception as e:
            print(f"Error reading purge countdown for group {group_num}: {e}")
            return None
    
    def is_machine_blocked(self):
        """Check if coffee machine is blocked"""
        try:
            result = self.client.read_holding_registers(address=269, count=1)
            if result.isError():
                return None
            return result.registers[0] == 1
        except Exception as e:
            print(f"Error reading machine block status: {e}")
            return None
    
    def get_number_of_groups(self):
        """Get total number of groups present"""
        try:
            result = self.client.read_holding_registers(address=270, count=1)
            if result.isError():
                return None
            return result.registers[0]
        except Exception as e:
            print(f"Error reading number of groups: {e}")
            return None
    
    # Group 2: Command Functions
    def send_coffee_command(self, group_num, command):
        """
        Send coffee delivery command to group (1-3)
        
        Commands:
        1 (0x0001): Single Short Coffee
        2 (0x0002): Single Long Coffee
        4 (0x0004): Double Short Coffee
        8 (0x0008): Double Long Coffee
        16 (0x0010): No Action
        32 (0x0020): Single Medium Coffee
        64 (0x0040): Double Medium Coffee
        128 (0x0080): Stop ongoing delivery
        256 (0x0100): Start Purge
        """
        if group_num < 1 or group_num > 3:
            raise ValueError("Group number must be 1-3")
        
        register_addr = 512 + (group_num - 1) 
        
        try:
            result = self.client.write_register(register_addr, command)
            return not result.isError()
        except Exception as e:
            print(f"Error sending command to group {group_num}: {e}")
            return False
    
    def deliver_single_short(self, group_num):
        """Deliver single short coffee"""
        return self.send_coffee_command(group_num, 1)
    
    def deliver_single_long(self, group_num):
        """Deliver single long coffee"""
        return self.send_coffee_command(group_num, 2)
    
    def deliver_double_short(self, group_num):
        """Deliver double short coffee"""
        return self.send_coffee_command(group_num, 4)
    
    def deliver_double_long(self, group_num):
        """Deliver double long coffee"""
        return self.send_coffee_command(group_num, 8)
    
    def deliver_single_medium(self, group_num):
        """Deliver single medium coffee"""
        return self.send_coffee_command(group_num, 32)
    
    def deliver_double_medium(self, group_num):
        """Deliver double medium coffee"""
        return self.send_coffee_command(group_num, 64)
    
    def stop_delivery(self, group_num):
        """Stop ongoing delivery"""
        return self.send_coffee_command(group_num, 128)
    
    def start_purge(self, group_num):
        """Start purge cycle"""
        return self.send_coffee_command(group_num, 256)
    
    def is_group_busy(self, group_num):
        """
        Check if a group is busy (has an ongoing delivery)
        Returns True if busy, False if free, None if error
        """
        if group_num < 1 or group_num > 3:  # Groups 1-3 as per documentation
            raise ValueError("Group number must be 1-3")
        
        # According to documentation, group status is in registers 256-258 (HEX 100-102)
        register_addr = 256 + (group_num - 1)  # Base address 256 (HEX 0x100) for group 1
        
        try:
            result = self.client.read_holding_registers(register_addr, count=1)
            if result.isError():
                return None
            
            status = result.registers[0]
            # Print status value for debugging
            print(f"Group {group_num} status register value: {status} (0x{status:04X})")
            
            # According to documentation, bits 0-7 indicate if a delivery is in progress
            # Check only the relevant bits (0-7) for coffee delivery
            delivery_mask = 0xFF  # Bits 0-7
            is_busy = (status & delivery_mask) != 0
            
            return is_busy
        except Exception as e:
            print(f"Error checking if group {group_num} is busy: {e}")
            return None
    
    def wait_until_group_is_free(self, group_num, timeout=30, check_interval=1.0):
        """
        Wait until the group is free (not busy with any delivery)
        
        Args:
            group_num: Group number (1-3)
            timeout: Maximum time to wait in seconds
            check_interval: How often to check in seconds
        
        Returns:
            True if group became free within timeout, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            busy = self.is_group_busy(group_num)
            
            if busy is None:
                print(f"Error checking group {group_num} status")
                return False
            
            if not busy:
                print(f"Group {group_num} is now free")
                return True
            
            print(f"Group {group_num} is busy, waiting...")
            time.sleep(check_interval)
        
        print(f"Timeout waiting for group {group_num} to become free")
        return False
    
    def send_water_command(self, set_num):
        """
        Send water delivery command
        set_num: 1 for SET 1, 2 for SET 2, 0 to stop
        """
        try:
            result = self.client.write_register(516, set_num)
            return not result.isError()
        except Exception as e:
            print(f"Error sending water command: {e}")
            return False
    
    def send_mat_command(self, set_num):
        """
        Send MAT delivery command
        set_num: 1 for SET 1, 2 for SET 2, 0 to stop
        """
        try:
            result = self.client.write_register(517, set_num)
            return not result.isError()
        except Exception as e:
            print(f"Error sending MAT command: {e}")
            return False

# Example usage
def main():
    # Initialize coffee machine (adjust port as needed)
    coffee_machine = LaSpazialeCoffeeMachine(port='COM4')  # Windows
    # coffee_machine = LaSpazialeCoffeeMachine(port='/dev/ttyUSB0')  # Linux
    
    if not coffee_machine.connect():
        print("Failed to connect to coffee machine")
        return
    
    try:
        # Read machine info
        print("=== Machine Information ===")
        serial = coffee_machine.get_serial_number()
        print(f"Serial Number: {serial}")
        
        firmware = coffee_machine.get_firmware_version()
        print(f"Firmware Version: {firmware}")
        
        num_groups = coffee_machine.get_number_of_groups()
        print(f"Number of Groups: {num_groups}")
        
        blocked = coffee_machine.is_machine_blocked()
        print(f"Machine Blocked: {blocked}")
        
        # Choose a group to use for coffee delivery
        group_to_use = 2  # Using group 2
        
        # Check initial status of all groups
        print("\n=== Initial Group Status ===")
        for group in range(1, num_groups + 1 if num_groups else 4):
            selection = coffee_machine.get_group_selection(group)
            fault = coffee_machine.get_sensor_fault(group)
            countdown = coffee_machine.get_purge_countdown(group)
            
            print(f"Group {group}:")
            print(f"  Current Selection: {selection}")
            print(f"  Sensor Fault: {fault}")
            print(f"  Purge Countdown: {countdown}s")
        
        # Read the status register directly to see what it contains
        print("\n=== Direct Register Reading ===")
        try:
            for reg_type, base_addr in [('Status', 256), ('Command', 512)]:
                print(f"\n{reg_type} Registers:")
                for i in range(3):  # Read for groups 1-3
                    addr = base_addr + i
                    result = coffee_machine.client.read_holding_registers(addr, count=1)
                    if not result.isError():
                        value = result.registers[0]
                        print(f"  Register {addr} (Group {i+1}): {value} (0x{value:04X})")
                    else:
                        print(f"  Error reading register {addr}")
        except Exception as e:
            print(f"Error during register reading: {e}")
        
        # Test sequence: Start purge -> wait for completion -> deliver coffee
        print("\n=== Coffee Delivery Test ===")
        
        # First check if group is busy before starting
        busy_before = coffee_machine.is_group_busy(group_to_use)
        print(f"Group {group_to_use} busy before starting: {busy_before}")
        
        # Send purge command
        print(f"Sending purge command to group {group_to_use}...")
        purge_result = coffee_machine.start_purge(group_to_use)
        print(f"Purge command sent: {purge_result}")
        
        # Wait a moment and check status
        print("Waiting 2 seconds...")
        time.sleep(2)
        busy_after_purge = coffee_machine.is_group_busy(group_to_use)
        print(f"Group {group_to_use} busy after purge command: {busy_after_purge}")
        
        # Read status register directly
        status_addr = 256 + (group_to_use - 1)
        try:
            result = coffee_machine.client.read_holding_registers(status_addr, count=1)
            if not result.isError():
                value = result.registers[0]
                print(f"Status register {status_addr} after purge: {value} (0x{value:04X})")
                print(f"Bits set: {''.join(['1' if (value & (1 << i)) else '0' for i in range(15, -1, -1)])}")
        except Exception as e:
            print(f"Error reading status register: {e}")
        
        # Wait for purge to complete
        print("Waiting for purge to complete...")
        if coffee_machine.wait_until_group_is_free(group_to_use, timeout=30):
            print(f"Group {group_to_use} is now free after purge")
            
            # Send coffee command
            print("Sending single long coffee command...")
            coffee_machine.stop_delivery(group_to_use)
            coffee_result = coffee_machine.deliver_single_long(group_to_use)
            print(f"Coffee command sent: {coffee_result}")
            
            # Check if group is busy right after sending command
            busy_after_coffee = coffee_machine.is_group_busy(group_to_use)
            print(f"Group {group_to_use} busy after coffee command: {busy_after_coffee}")
            
            # Read status register directly
            try:
                result = coffee_machine.client.read_holding_registers(status_addr, count=1)
                if not result.isError():
                    value = result.registers[0]
                    print(f"Status register {status_addr} after coffee command: {value} (0x{value:04X})")
                    print(f"Bits set: {''.join(['1' if (value & (1 << i)) else '0' for i in range(15, -1, -1)])}")
            except Exception as e:
                print(f"Error reading status register: {e}")
        else:
            print(f"Warning: Group {group_to_use} did not become free within timeout period")
        
        # Final status check
        print("\n=== Final Group Status ===")
        selection = coffee_machine.get_group_selection(group_to_use)
        print(f"Group {group_to_use} final status: {selection}")

    
    finally:
        coffee_machine.disconnect()
        coffee_machine.client.close()
        print("\n=== Coffee Delivery Completed ===")

if __name__ == "__main__":
    main()
    # TODO: add try catch block
    # TODO: add logging
    # TODO: add command line arguments
    # TODO: add documentation