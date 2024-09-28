import socket
import struct

# Define the packet format based on your provided struct
packet_format = 'i f f f i i f f'  # Adjust this format based on your struct definition

# Define the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 9995))  # Replace with your IP and port

def parse_data(data):
    try:
        # Unpack the data according to the format string
        unpacked_data = struct.unpack(packet_format, data[:struct.calcsize(packet_format)])
        
        # Extract individual values from the unpacked data
        packet_id, gas, brake, fuel, gear, rpm, steering_angle, speed = unpacked_data
        
        # Print the extracted values
        print(f"Packet ID: {packet_id}")
        print(f"Gas: {gas}")
        print(f"Brake: {brake}")
        print(f"Fuel: {fuel}")
        print(f"Gear: {gear}")
        print(f"RPM: {rpm}")
        print(f"Steering Angle: {steering_angle}")
        print(f"Speed: {speed} km/h")
        
    except struct.error as e:
        print(f"Error unpacking data: {e}")

def receive_data():
    while True:
        data, addr = sock.recvfrom(600)  # Expecting 600 bytes (adjust if necessary)
        print(f"Received data size: {len(data)} bytes")
        if len(data) == 600:
            parse_data(data)
        else:
            print(f"Received incorrect data size: {len(data)} bytes")

if __name__ == "__main__":
    receive_data()

# Define the packet format based on 672 bytes
packet_format = (
    'c i f f f ? ? ? ? ? ? '  # 23 bytes: 1 byte (char) + 4 bytes (int) + 12 bytes (floats) + 6 bytes (bools)
    'f f f i i i i f f f f f f f f f f '  # 40 bytes: 12 bytes (floats) + 12 bytes (ints) + 16 bytes (floats)
    'f f f f f f f f f f f f f f f f f f '  # 64 bytes: 16 bytes (floats) * 4
    'f f f f f f f f f f f f f f f f f f '  # 64 bytes: 16 bytes (floats) * 4
    'f f f f f f f f f f f f f f f f f f '  # 64 bytes: 16 bytes (floats) * 4
    'f f f f f f f f f f f f f f f f f f '  # 64 bytes: 16 bytes (floats) * 4
    'f f f f f f f f f f f f f f f f f f '  # 64 bytes: 16 bytes (floats) * 4
    'f f f f f f f f f f f f f f f f f f '  # 64 bytes: 16 bytes (floats) * 4
)

def parse_data(data):
    try:
        # Unpack the data according to the format string
        unpacked_data = struct.unpack(packet_format, data[:struct.calcsize(packet_format)])
        
        # Extract individual values from the unpacked data
        packet_id, gas, brake, fuel, gear, rpm, steering_angle, speed = unpacked_data
        
        # Print the extracted values
        print(f"Packet ID: {packet_id}")
        print(f"Gas: {gas}")
        print(f"Brake: {brake}")
        print(f"Fuel: {fuel}")
        print(f"Gear: {gear}")
        print(f"RPM: {rpm}")
        print(f"Steering Angle: {steering_angle}")
        print(f"Speed: {speed} km/h")
        
    except struct.error as e:
        print(f"Error unpacking data: {e}")

def receive_data():
    while True:
        data, addr = sock.recvfrom(600)  # Expecting 600 bytes (adjust if necessary)
        print(f"Received data size: {len(data)} bytes")
        if len(data) == 600:
            parse_data(data)
        else:
            print(f"Received incorrect data size: {len(data)} bytes")

if __name__ == "__main__":
    receive_data()
