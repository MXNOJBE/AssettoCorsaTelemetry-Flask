import ctypes 
from ctypes import *
import time
import mmap
import json
from flask import Flask, jsonify, render_template
from dataRepository import SPageFileStatic, SPageFilePhysics, SPageFileGraphic

app = Flask(__name__)

# Memory-mapped files
physics = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "Local\\acpmf_physics")
miscellaneous = mmap.mmap(0, ctypes.sizeof(SPageFileStatic), "Local\\acpmf_static")
graphics = mmap.mmap(0, ctypes.sizeof(SPageFileGraphic), "Local\\acpmf_graphics")

gearCount = 0
previousGear = -1
previousSessionList = []
oldRaceData = {}
liveRaceData = {}
previousStatus = 0
lapInfo = {}
carInfo = {}

PREVIOUS_SESSIONS_FILE = 'previous_sessions.json'

def read_graphics_data():
    graphics.seek(0)
    return SPageFileGraphic.from_buffer_copy(graphics.read(ctypes.sizeof(SPageFileGraphic)))

def read_physics_data():
    physics.seek(0)
    return SPageFilePhysics.from_buffer_copy(physics.read(ctypes.sizeof(SPageFilePhysics)))

def read_player_data():
    miscellaneous.seek(0)
    return SPageFileStatic.from_buffer_copy(miscellaneous.read(ctypes.sizeof(SPageFileStatic)))

def load_previous_sessions():
    global previousSessionList
    try:
        with open(PREVIOUS_SESSIONS_FILE, 'r') as file:
            previousSessionList = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        previousSessionList = []

def save_previous_sessions():
    with open(PREVIOUS_SESSIONS_FILE, 'w') as file:
        json.dump(previousSessionList, file)


@app.route('/web')
def index():
    return render_template('index.html')

def serialize_data(data):
    serialized = {}
    for field_name, field_type in data._fields_:
        value = getattr(data, field_name)
        if isinstance(value, ctypes.Array):
            serialized[field_name] = list(value)
        else:
            serialized[field_name] = value
    return serialized

@app.route('/update') 
def update_data():
    global previousGear, gearCount, oldRaceData, previousSessionList, previousStatus, telemetry_data, lapInfo, carInfo
    
    physics_json = read_physics_data()
    static_json = read_player_data()
    graphics_json = read_graphics_data()
    currentGear = physics_json.gear - 1
    
    physics_json = serialize_data(physics_json)
    graphics_json = serialize_data(graphics_json)
    static_json = serialize_data(static_json)

    if currentGear != previousGear and previousGear != -1:
        gearCount += 1
    previousGear = currentGear

    if previousStatus != 0 and graphics_json['status'] == 0 and graphics_json['session'] == 0:

        carInfo = {
            "gas": physics_json['gas'],
            "brake": physics_json['brake'],
            "fuel": physics_json['fuel'],
            "gear": physics_json['gear'],
            "rpms": physics_json['rpms'],
            "steerAngle": physics_json['steerAngle'],
            "speedKmh": physics_json['speedKmh'],
            "velocity": physics_json['velocity'],
            "accG": physics_json['accG'],
            "wheelSlip": physics_json['wheelSlip'],
            "wheelLoad": physics_json['wheelLoad'],
            "wheelsPressure": physics_json['wheelsPressure'],
            "wheelAngularSpeed": physics_json['wheelAngularSpeed'],
            "tyreWear": physics_json['tyreWear'],
            "tyreDirtyLevel": physics_json['tyreDirtyLevel'],
            "tyreCoreTemperature": physics_json['tyreCoreTemperature'],
            "camberRAD": physics_json['camberRAD'],
            "suspensionTravel": physics_json['suspensionTravel'],
            "drs": physics_json['drs'],
            "tc": physics_json['tc'],
            "heading": physics_json['heading'],
            "pitch": physics_json['pitch'],
            "roll": physics_json['roll'],
            "cgHeight": physics_json['cgHeight'],
            "carDamage": physics_json['carDamage'],
            "numberOfTyresOut": physics_json['numberOfTyresOut'],
            "pitLimiterOn": physics_json['pitLimiterOn'],
            "abs": physics_json['abs'],
            "kersCharge": physics_json['kersCharge'],
            "kersInput": physics_json['kersInput'],
            "autoShifterOn": physics_json['autoShifterOn'],
            "rideHeight": physics_json['rideHeight'],
            "turboBoost": physics_json['turboBoost'],
            "ballast": physics_json['ballast'],
            "airDensity": physics_json['airDensity'],
            "airTemp": physics_json['airTemp'],
            "roadTemp": physics_json['roadTemp'],
            "localAngularVel": physics_json['localAngularVel'],
            "finalFF": physics_json['finalFF'],
            "performanceMeter": physics_json['performanceMeter'],
            "engineBrake": physics_json['engineBrake'],
            "ersRecoveryLevel": physics_json['ersRecoveryLevel'],
            "ersPowerLevel": physics_json['ersPowerLevel'],
            "ersHeatCharging": physics_json['ersHeatCharging'],
            "ersIsCharging": physics_json['ersIsCharging'],
            "kersCurrentKJ": physics_json['kersCurrentKJ'],
            "drsAvailable": physics_json['drsAvailable'],
            "drsEnabled": physics_json['drsEnabled'],
            "brakeTemp": physics_json['brakeTemp'],
            "clutch": physics_json['clutch'],
            "isAIControlled": physics_json['isAIControlled'],
            "brakeBias": physics_json['brakeBias'],
            "localVelocity": physics_json['localVelocity']
}

        
        lapInfo = {
            "status": graphics_json['status'],
            "session": graphics_json['session'],
            "currentTime": graphics_json['currentTime'],
            "lastTime": graphics_json['lastTime'],
            "bestTime": graphics_json['bestTime'],
            "split": graphics_json['split'],
            "completedLaps": graphics_json['completedLaps'],
            "position": graphics_json['position'],
            "iCurrentTime": graphics_json['iCurrentTime'],
            "iLastTime": graphics_json['iLastTime'],
            "iBestTime": graphics_json['iBestTime'],
            "sessionTimeLeft": graphics_json['sessionTimeLeft'],
            "distanceTraveled": graphics_json['distanceTraveled'],
            "isInPit": graphics_json['isInPit'],
            "currentSectorIndex": graphics_json['currentSectorIndex'],
            "lastSectorTime": graphics_json['lastSectorTime'],
            "numberOfLaps": graphics_json['numberOfLaps'],
            "tyreCompound": graphics_json['tyreCompound'],
            "replayTimeMultiplier": graphics_json['replayTimeMultiplier'],
            "normalizedCarPosition": graphics_json['normalizedCarPosition'],
            "carCoordinates": graphics_json['carCoordinates'],
            "penaltyTime": graphics_json['penaltyTime'],
            "flag": graphics_json['flag'],
            "idealLineOn": graphics_json['idealLineOn'],
            "isInPitLane": graphics_json['isInPitLane'],
            "surfaceGrip": graphics_json['surfaceGrip'],
            "mandatoryPitDone": graphics_json['mandatoryPitDone'],
            "windSpeed": graphics_json['windSpeed'],
            "windDirection": graphics_json['windDirection'],
            "carData": carInfo
}
        
        oldRaceData = {
            "numCars": static_json['numCars'],
            "carModel": static_json['carModel'],
            "track": static_json['track'],
            "playerName": static_json['playerName'],
            "playerSurname": static_json['playerSurname'],
            "playerNick": static_json['playerNick'],
            "sectorCount": static_json['sectorCount'],
            "maxTorque": static_json['maxTorque'],
            "maxPower": static_json['maxPower'],
            "maxRpm": static_json['maxRpm'],
            "maxFuel": static_json['maxFuel'],
            "suspensionMaxTravel": static_json['suspensionMaxTravel'],
            "tyreRadius": static_json['tyreRadius'],
            "maxTurboBoost": static_json['maxTurboBoost'],
            "airTemp": static_json['airTemp'],
            "roadTemp": static_json['roadTemp'],
            "penaltiesEnabled": static_json['penaltiesEnabled'],
            "aidFuelRate": static_json['aidFuelRate'],
            "aidTireRate": static_json['aidTireRate'],
            "aidMechanicalDamage": static_json['aidMechanicalDamage'],
            "aidAllowTyreBlankets": static_json['aidAllowTyreBlankets'],
            "aidStability": static_json['aidStability'],
            "aidAutoClutch": static_json['aidAutoClutch'],
            "aidAutoBlip": static_json['aidAutoBlip'],
            "hasDRS": static_json['hasDRS'],
            "hasERS": static_json['hasERS'],
            "hasKERS": static_json['hasKERS'],
            "kersMaxJ": static_json['kersMaxJ'],
            "engineBrakeSettingsCount": static_json['engineBrakeSettingsCount'],
            "ersPowerControllerCount": static_json['ersPowerControllerCount'],
            "trackSPlineLength": static_json['trackSPlineLength'],
            "trackConfiguration": static_json['trackConfiguration'],
            "ersMaxJ": static_json['ersMaxJ'],
            "isTimedRace": static_json['isTimedRace'],
            "hasExtraLap": static_json['hasExtraLap'],
            "carSkin": static_json['carSkin'],
            "reversedGridPositions": static_json['reversedGridPositions'],
            "pitWindowStart": static_json['pitWindowStart'],
            "pitWindowEnd": static_json['pitWindowEnd'],
            "lapInfo": lapInfo,
            "carInfo": carInfo
        }

        previousSessionList.append(oldRaceData)
        try:
            save_previous_sessions()
        except Exception as e:
            print("Error saving sessions:", e)

        gearCount = 0 
        previousStatus = 0
        
    liveRaceData = {
            "numCars": static_json['numCars'],
            "carModel": static_json['carModel'],
            "track": static_json['track'],
            "playerName": static_json['playerName'],
            "playerSurname": static_json['playerSurname'],
            "playerNick": static_json['playerNick'],
            "sectorCount": static_json['sectorCount'],
            "maxTorque": static_json['maxTorque'],
            "maxPower": static_json['maxPower'],
            "maxRpm": static_json['maxRpm'],
            "maxFuel": static_json['maxFuel'],
            "suspensionMaxTravel": static_json['suspensionMaxTravel'],
            "tyreRadius": static_json['tyreRadius'],
            "maxTurboBoost": static_json['maxTurboBoost'],
            "airTemp": static_json['airTemp'],
            "roadTemp": static_json['roadTemp'],
            "penaltiesEnabled": static_json['penaltiesEnabled'],
            "aidFuelRate": static_json['aidFuelRate'],
            "aidTireRate": static_json['aidTireRate'],
            "aidMechanicalDamage": static_json['aidMechanicalDamage'],
            "aidAllowTyreBlankets": static_json['aidAllowTyreBlankets'],
            "aidStability": static_json['aidStability'],
            "aidAutoClutch": static_json['aidAutoClutch'],
            "aidAutoBlip": static_json['aidAutoBlip'],
            "hasDRS": static_json['hasDRS'],
            "hasERS": static_json['hasERS'],
            "hasKERS": static_json['hasKERS'],
            "kersMaxJ": static_json['kersMaxJ'],
            "engineBrakeSettingsCount": static_json['engineBrakeSettingsCount'],
            "ersPowerControllerCount": static_json['ersPowerControllerCount'],
            "trackSPlineLength": static_json['trackSPlineLength'],
            "trackConfiguration": static_json['trackConfiguration'],
            "ersMaxJ": static_json['ersMaxJ'],
            "isTimedRace": static_json['isTimedRace'],
            "hasExtraLap": static_json['hasExtraLap'],
            "carSkin": static_json['carSkin'],
            "reversedGridPositions": static_json['reversedGridPositions'],
            "pitWindowStart": static_json['pitWindowStart'],
            "pitWindowEnd": static_json['pitWindowEnd'],
            "status": graphics_json['status'],
            "session": graphics_json['session'],
            "currentTime": graphics_json['currentTime'],
            "lastTime": graphics_json['lastTime'],
            "bestTime": graphics_json['bestTime'],
            "split": graphics_json['split'],
            "completedLaps": graphics_json['completedLaps'],
            "position": graphics_json['position'],
            "iCurrentTime": graphics_json['iCurrentTime'],
            "iLastTime": graphics_json['iLastTime'],
            "iBestTime": graphics_json['iBestTime'],
            "sessionTimeLeft": graphics_json['sessionTimeLeft'],
            "distanceTraveled": graphics_json['distanceTraveled'],
            "isInPit": graphics_json['isInPit'],
            "currentSectorIndex": graphics_json['currentSectorIndex'],
            "lastSectorTime": graphics_json['lastSectorTime'],
            "numberOfLaps": graphics_json['numberOfLaps'],
            "tyreCompound": graphics_json['tyreCompound'],
            "replayTimeMultiplier": graphics_json['replayTimeMultiplier'],
            "normalizedCarPosition": graphics_json['normalizedCarPosition'],
            "carCoordinates": graphics_json['carCoordinates'],
            "penaltyTime": graphics_json['penaltyTime'],
            "flag": graphics_json['flag'],
            "idealLineOn": graphics_json['idealLineOn'],
            "isInPitLane": graphics_json['isInPitLane'],
            "surfaceGrip": graphics_json['surfaceGrip'],
            "mandatoryPitDone": graphics_json['mandatoryPitDone'],
            "windSpeed": graphics_json['windSpeed'],
            "windDirection": graphics_json['windDirection'],
            "gas": physics_json['gas'],
            "brake": physics_json['brake'],
            "fuel": physics_json['fuel'],
            "gear": physics_json['gear'],
            "rpms": physics_json['rpms'],
            "steerAngle": physics_json['steerAngle'],
            "speedKmh": physics_json['speedKmh'],
            "velocity": physics_json['velocity'],
            "accG": physics_json['accG'],
            "wheelSlip": physics_json['wheelSlip'],
            "wheelLoad": physics_json['wheelLoad'],
            "wheelsPressure": physics_json['wheelsPressure'],
            "wheelAngularSpeed": physics_json['wheelAngularSpeed'],
            "tyreWear": physics_json['tyreWear'],
            "tyreDirtyLevel": physics_json['tyreDirtyLevel'],
            "tyreCoreTemperature": physics_json['tyreCoreTemperature'],
            "camberRAD": physics_json['camberRAD'],
            "suspensionTravel": physics_json['suspensionTravel'],
            "drs": physics_json['drs'],
            "tc": physics_json['tc'],
            "heading": physics_json['heading'],
            "pitch": physics_json['pitch'],
            "roll": physics_json['roll'],
            "cgHeight": physics_json['cgHeight'],
            "carDamage": physics_json['carDamage'],
            "numberOfTyresOut": physics_json['numberOfTyresOut'],
            "pitLimiterOn": physics_json['pitLimiterOn'],
            "abs": physics_json['abs'],
             "kersCharge": physics_json['kersCharge'],
            "kersInput": physics_json['kersInput'],
            "autoShifterOn": physics_json['autoShifterOn'],
            "rideHeight": physics_json['rideHeight'],
            "turboBoost": physics_json['turboBoost'],
            "ballast": physics_json['ballast'],
             "airDensity": physics_json['airDensity'],
            "airTemp": physics_json['airTemp'],
            "roadTemp": physics_json['roadTemp'],
            "localAngularVel": physics_json['localAngularVel'],
            "finalFF": physics_json['finalFF'],
            "performanceMeter": physics_json['performanceMeter'],
            "engineBrake": physics_json['engineBrake'],
            "ersRecoveryLevel": physics_json['ersRecoveryLevel'],
            "ersPowerLevel": physics_json['ersPowerLevel'],
            "ersHeatCharging": physics_json['ersHeatCharging'],
            "ersIsCharging": physics_json['ersIsCharging'],
            "kersCurrentKJ": physics_json['kersCurrentKJ'],
            "drsAvailable": physics_json['drsAvailable'],
            "drsEnabled": physics_json['drsEnabled'],
            "brakeTemp": physics_json['brakeTemp'],
            "isAIControlled": physics_json['isAIControlled'],
            "brakeBias": physics_json['brakeBias'],
            "localVelocity": physics_json['localVelocity']

    }

    previousStatus = graphics_json['status']
    return jsonify(liveRaceData)


@app.route('/previousSessions')
def previousSessions():
    global previousSessionList
    return jsonify(previousSessionList)

if __name__ == '__main__':
    load_previous_sessions()
    app.run(debug=True)