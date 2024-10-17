import time
import mmap
import ctypes
from flask import Flask, jsonify, render_template
from flask import Response
import json
from dataRepository import SPageFileStatic, SPageFilePhysics, SPageFileGraphic

app = Flask(__name__)

physics = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "Local\\acpmf_physics")
miscellaneous = mmap.mmap(0, ctypes.sizeof(SPageFileStatic), "Local\\acpmf_static")
graphics = mmap.mmap(0, ctypes.sizeof(SPageFileGraphic), "Local\\acpmf_graphics")

gearCount = 0
previousGear = -1
previousSessionList = []
old_telemetry_data = {}
previousStatus = 0

def read_graphics_data():
    graphics.seek(0)
    return SPageFileGraphic.from_buffer_copy(graphics.read(ctypes.sizeof(SPageFileGraphic)))

def read_physics_data():
    physics.seek(0)
    return SPageFilePhysics.from_buffer_copy(physics.read(ctypes.sizeof(SPageFilePhysics)))

def read_player_data():
    miscellaneous.seek(0)
    return SPageFileStatic.from_buffer_copy(miscellaneous.read(ctypes.sizeof(SPageFileStatic)))


@app.route('/web')
def index():
    return render_template('index.html')

@app.route('/update') 
def update_data():
    global previousGear, gearCount, old_telemetry_data, previousSessionList, previousStatus, telemetry_data

    physicsData = read_physics_data()
    playerData = read_player_data()
    graphicsData = read_graphics_data()
    currentGear = physicsData.gear - 1

    # Track gear count
    if currentGear != previousGear and previousGear != -1:
        gearCount += 1
    previousGear = currentGear

    # Store session data if a session has ended
    if previousStatus != 0 and graphicsData.status == 0 and graphicsData.session == 0:
        # Save the last session's telemetry data
        old_telemetry_data = {
            "gear": currentGear,
            "rpms": physicsData.rpms,
            "steerAngle": physicsData.steerAngle,
            "speedKmh": physicsData.speedKmh,
            "gearCount": gearCount,
            "playerName": playerData.playerName, 
            "carModel": playerData.carModel,
            "maxPower": playerData.maxPower,
            "status": graphicsData.status,
            "session": graphicsData.session
        }
        previousSessionList.append(old_telemetry_data)
        gearCount = 0 
        previousStatus = 0  # Reset status

    else:
        # Keep updating the telemetry data for an ongoing session
        telemetry_data = {
            "gear": currentGear,
            "rpms": physicsData.rpms,
            "steerAngle": physicsData.steerAngle,
            "speedKmh": physicsData.speedKmh,
            "gearCount": gearCount,
            "playerName": playerData.playerName, 
            "carModel": playerData.carModel,
            "maxPower": playerData.maxPower,
            "status": graphicsData.status,
            "session": graphicsData.session
        }
        previousStatus = graphicsData.status  # Keep track of the status for next update

    return jsonify(telemetry_data)


@app.route('/previousSessions')
def previousSessions():
    global previousSessionList
    return jsonify(previousSessionList)


if __name__ == '__main__':
    app.run(debug=True)
