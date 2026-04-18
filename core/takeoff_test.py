import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time


ip = 'udp:127.0.0.1:14550' 
vehicle = connect(ip, wait_ready=True)

if vehicle:
   print("baglandi") 

def goto(enlem, boylam, irtifa):
    if vehicle.mode.name != "GUIDED":
        vehicle.mode = VehicleMode("GUIDED")
        while not vehicle.mode.name == 'GUIDED':
            time.sleep(1)
            
    hedef_konum = LocationGlobalRelative(enlem, boylam, irtifa)
    
    vehicle.simple_goto(hedef_konum)
    print(f"hedefe gidiyor...\nenlem: {enlem},\nboylam: {boylam},\nirtifa: {irtifa}\n")

goto(41.015137, 28.979530, 50)

def arm_and_takeoff(aTargetAltitude):

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

arm_and_takeoff(0.2)
