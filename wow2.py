import socket
import struct

UDP_IP = "127.0.0.1"
UDP_PORT = 9995

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

previous_gear = -1

while True:
    data, addr = sock.recvfrom(4096)
    gear = struct.unpack_from('B', data, 90)[0]  # Gear at offset 20

    if gear != previous_gear:
        print(f"Gear changed to: {gear}")
        previous_gear = gear
