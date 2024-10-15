import time
import mmap
import ctypes
from flask import Flask, jsonify, render_template
from flask import Response
from system.dataRepository import SPageFileStatic, SPageFilePhysics, SPageFileGraphic


app = Flask(__name__)


physics = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "Local\\acpmf_physics")
miscellaneous = mmap.mmap(0, ctypes.sizeof(SPageFileStatic), "Local\\acpmf_static")
graphics = mmap.mmap(0, ctypes.sizeof(SPageFileGraphic), "Local\\acpmf_graphics")

gearCount = 0
previousGear = -1

def read_graphics_data():
    graphics.seek(0)
    return SPageFileGraphic.from_buffer_copy(graphics.read(ctypes.sizeof(SPageFileGraphic)))

def read_physics_data():
    physics.seek(0)
    return SPageFilePhysics.from_buffer_copy(physics.read(ctypes.sizeof(SPageFilePhysics)))

def read_player_data():
    miscellaneous.seek(0)
    return SPageFileStatic.from_buffer_copy(miscellaneous.read(ctypes.sizeof(SPageFileStatic)))


@app.route('/live')
def index():
    return render_template('index.html')

@app.route('/') 
def update_data():
    global previousGear, gearCount
    data = read_physics_data()
    playerData = read_player_data()
    currentGear = data.gear - 1
    if currentGear != previousGear and previousGear != -1:
        gearCount += 1

    previousGear = currentGear

    telemetry_data = {
        "gear": currentGear,
        "rpms": data.rpms,
        "steerAngle": data.steerAngle,
        "speedKmh": data.speedKmh,
        "gearCount": gearCount,
        "playerName": playerData.playerName, 
        "carModel": playerData.carModel,
        "maxPower": playerData.maxPower
    }
    
    return jsonify(telemetry_data)

if __name__ == '__main__':
    app.run(debug=True)
