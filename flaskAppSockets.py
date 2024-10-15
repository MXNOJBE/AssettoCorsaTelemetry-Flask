from flask import Flask
from flask_socketio import SocketIO
import time
import ctypes
import mmap
import signal
from system.dataRepository import SPageFileStatic, SPageFilePhysics, SPageFileGraphic

app = Flask(__name__)
socketio = SocketIO(app)

physics = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "Local\\acpmf_physics")
miscellaneous = mmap.mmap(0, ctypes.sizeof(SPageFileStatic), "Local\\acpmf_static")
graphics = mmap.mmap(0, ctypes.sizeof(SPageFileGraphic), "Local\\acpmf_graphics")

def read_physics_data():
    try:
        physics.seek(0)
        return SPageFilePhysics.from_buffer_copy(physics.read(ctypes.sizeof(SPageFilePhysics)))
    except Exception as e:
        print(f"Error reading physics data: {e}")

def read_player_data():
    try:
        miscellaneous.seek(0)
        return SPageFileStatic.from_buffer_copy(miscellaneous.read(ctypes.sizeof(SPageFileStatic)))
    except Exception as e:
        print(f"Error reading player data: {e}")

@socketio.on('connect')
def connect():
    print("Client connected")

@socketio.on('disconnect')
def disconnect():
    print("Client disconnected")

def send_telemetry_data():
    while True:
        data = read_physics_data()
        player_data = read_player_data()
        telemetry_data = {
            "gear": data.gear - 1,
            "rpms": data.rpms,
            "speedKmh": data.speedKmh,
            "playerName": player_data.playerName,
            "carModel": player_data.carModel
        }
        socketio.emit('telemetry', telemetry_data)
        socketio.sleep(0.1)

def shutdown_handler(signum, frame):
    socketio.stop()

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == '__main__':
    socketio.start_background_task(send_telemetry_data)
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
