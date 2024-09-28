import struct

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
    print(f"Received data size: {len(data)} bytes")
    try:
        unpacked_data = struct.unpack(packet_format, data)
        
        # Extract fields as needed
        gear = unpacked_data[19]
        gas = unpacked_data[11]
        brake = unpacked_data[12]
        engineRPM = unpacked_data[13]
        
        print(f'Gear: {gear}, Gas: {gas}, Brake: {brake}, Engine RPM: {engineRPM}')
    except struct.error as e:
        print(f'Error unpacking data: {e}')

# Example usage
# Simulate receiving a packet
data = b'\x00' * 672  # Replace with actual data
parse_data(data)
