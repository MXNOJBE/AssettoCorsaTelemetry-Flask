import time
import mmap
import ctypes
import tkinter as tk
from tkinter import ttk
from flaskapp import uploadGearData


class SPageFilePhysics(ctypes.Structure):
    _fields_ = [
        ("packetId", ctypes.c_int),             # Unique identifier for the packet
        ("gas", ctypes.c_float),                # Amount of throttle input (0.0 to 1.0)
        ("brake", ctypes.c_float),              # Amount of brake input (0.0 to 1.0)
        ("fuel", ctypes.c_float),               # Amount of fuel left in liters
        ("gear", ctypes.c_int),                 # Current gear (-1 = reverse, 0 = neutral, 1+ = forward gears)
        ("rpms", ctypes.c_int),                 # Engine RPM
        ("steerAngle", ctypes.c_float),         # Steering angle in degrees
        ("speedKmh", ctypes.c_float),           # Current speed in km/h
        ("velocity", ctypes.c_float * 3),       # Velocity in the world (X, Y, Z components)
        ("accG", ctypes.c_float * 3),           # Acceleration in G forces (X, Y, Z components)
        ("wheelSlip", ctypes.c_float * 4),      # Slip ratio for each wheel
        ("wheelLoad", ctypes.c_float * 4),      # Load on each wheel
        ("wheelsPressure", ctypes.c_float * 4), # Tire pressures for each wheel
        ("wheelAngularSpeed", ctypes.c_float * 4), # Angular speed of each wheel
        ("tyreWear", ctypes.c_float * 4),       # Tire wear percentage for each wheel
        ("tyreDirtyLevel", ctypes.c_float * 4), # Tire dirt level for each wheel
        ("tyreCoreTemperature", ctypes.c_float * 4), # Core temperature for each tire
        ("camberRAD", ctypes.c_float * 4),      # Camber angle for each wheel in radians
        ("suspensionTravel", ctypes.c_float * 4), # Suspension travel for each wheel
        ("drs", ctypes.c_float),                # DRS (Drag Reduction System) status (0.0 = closed, 1.0 = open)
        ("tc", ctypes.c_float),                 # Traction control level
        ("heading", ctypes.c_float),            # Heading of the car in radians
        ("pitch", ctypes.c_float),              # Pitch angle of the car in radians
        ("roll", ctypes.c_float),               # Roll angle of the car in radians
        ("cgHeight", ctypes.c_float),           # Height of the center of gravity
        ("carDamage", ctypes.c_float * 5),      # Car damage for 5 different parts
        ("pitLimiterOn", ctypes.c_int),         # Pit limiter status (1 = on, 0 = off)
        ("abs", ctypes.c_float),                # ABS (Anti-lock Braking System) level
        ("kersCharge", ctypes.c_float),         # KERS (Kinetic Energy Recovery System) charge level
        ("kersInput", ctypes.c_float),          # KERS input level
        ("autoShifterOn", ctypes.c_int),        # Automatic shifter status (1 = on, 0 = off)
        ("rideHeight", ctypes.c_float * 2),     # Ride height for the front and rear suspension
        ("turboBoost", ctypes.c_float),         # Turbo boost level
        ("ballast", ctypes.c_float),            # Ballast weight added to the car
        ("airDensity", ctypes.c_float),         # Air density at current altitude
        ("airTemp", ctypes.c_float),            # Air temperature in degrees Celsius
        ("roadTemp", ctypes.c_float),           # Road temperature in degrees Celsius
        ("localAngularVel", ctypes.c_float * 3),# Local angular velocity of the car (pitch, yaw, roll)
        ("finalFF", ctypes.c_float),            # Final force feedback strength
        ("performanceMeter", ctypes.c_float),   # Performance meter value
        ("engineBrake", ctypes.c_int),          # Engine braking level
        ("ersRecoveryLevel", ctypes.c_int),     # ERS (Energy Recovery System) recovery level
        ("ersPowerLevel", ctypes.c_int),        # ERS power delivery level
        ("ersHeatCharging", ctypes.c_int),      # ERS heat-based charging status
        ("ersIsCharging", ctypes.c_int),        # ERS charging status (1 = charging, 0 = not charging)
        ("kersCurrentKJ", ctypes.c_float),      # Current KERS energy in kilojoules
        ("drsAvailable", ctypes.c_int),         # DRS availability (1 = available, 0 = not available)
        ("drsEnabled", ctypes.c_int),           # DRS enabled (1 = enabled, 0 = disabled)
        ("brakeTemp", ctypes.c_float * 4),      # Brake temperatures for each wheel
        ("clutch", ctypes.c_float),             # Clutch input level (0.0 to 1.0)
        ("tyreTempI", ctypes.c_float * 4),      # Inner tire temperature for each wheel
        ("tyreTempM", ctypes.c_float * 4),      # Middle tire temperature for each wheel
        ("tyreTempO", ctypes.c_float * 4),      # Outer tire temperature for each wheel
        ("isAIControlled", ctypes.c_int),       # Whether the car is being controlled by AI (1 = AI, 0 = player)
        ("tyreContactPoint", ctypes.c_float * 4 * 3),  # Contact point of each tire with the road (X, Y, Z)
        ("tyreContactNormal", ctypes.c_float * 4 * 3), # Normal vector of tire contact with the road (X, Y, Z)
        ("tyreContactHeading", ctypes.c_float * 4 * 3), # Heading of the tire contact point (X, Y, Z)
        ("brakeBias", ctypes.c_float),          # Brake bias percentage (front/rear)
    ]


def read_physics_data():
    # Read telemetry data from shared memory
    physics.seek(0)
    return SPageFilePhysics.from_buffer_copy(physics.read(ctypes.sizeof(SPageFilePhysics)))

gearCount = 0
previousGear = -1
brakeCount = 0

def update_gui():
    global previousGear, gearCount
    # Update the GUI with telemetry data
    data = read_physics_data()
    print(f"Previous Gear {previousGear}")
    gear_var.set(f"Gear: {data.gear - 1}")
    currentGear = data.gear - 1
    print(f"Current Gear {currentGear}")
    if currentGear != previousGear and previousGear!=-1:
        print("Gear Changed")
        gearCount = gearCount + 1
        gearCountData = {
            "gear": gearCount
        }
        uploadGearData(gearCountData.jsonify())
        print("-----------------------------------------------")
        gearCountVar.set(f"Total Gear Changes: {gearCount}")
        

    previousGear = currentGear
    rpm_var.set(f"RPM: {data.rpms}")
    steer_angle_var.set(f"Steering Angle: {data.steerAngle:.2f}°")
    speed_var.set(f"Speed: {data.speedKmh:.2f} km/h")
    

    # Schedule the function to run again after 1000 milliseconds
    root.after(1000, update_gui)

# Memory map initialization for Assetto Corsa telemetry data
physics = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "Local\\acpmf_physics")

# Initialize Tkinter window
root = tk.Tk()
root.title("Assetto Corsa Telemetry")

# Define StringVar for each data type to display dynamically
gear_var = tk.StringVar()
rpm_var = tk.StringVar()
steer_angle_var = tk.StringVar()
speed_var = tk.StringVar()
gearCountVar = tk.StringVar()


# Create labels to display telemetry data
gear_label = ttk.Label(root, textvariable=gear_var, font=("Arial", 16))
rpm_label = ttk.Label(root, textvariable=rpm_var, font=("Arial", 16))
steer_angle_label = ttk.Label(root, textvariable=steer_angle_var, font=("Arial", 16))
speed_label = ttk.Label(root, textvariable=speed_var, font=("Arial", 16))
gear_count_label = ttk.Label(root, textvariable=gearCountVar, font=("Arial", 16))

# Position the labels in the window
gear_label.pack(pady=10)
rpm_label.pack(pady=10)
steer_angle_label.pack(pady=10)
speed_label.pack(pady=10)
gear_count_label.pack(pady=10)

# Call the update function to start updating data
update_gui()

# Start the Tkinter main loop
root.mainloop()


