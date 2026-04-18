import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time


ip = 'udp:127.0.0.1:14550'
vehicle = connect(ip, wait_ready=True)

if vehicle:
   print("baglandi")


print ("Autopilot Firmware version:", vehicle.version)
print ("Global Location: ", vehicle.location.global_frame)
print ("Global Location (relative altitude): ", vehicle.location.global_relative_frame)
print ("Local Location: ", vehicle.location.local_frame)
print ("Attitude: ", vehicle.attitude)
print ("Velocity: ", vehicle.velocity)
print ("GPS: ", vehicle.gps_0)
print ("Groundspeed: ", vehicle.groundspeed)
print ("Airspeed: ", vehicle.airspeed)
print ("Gimbal status: ", vehicle.gimbal)
print ("Battery: ", vehicle.battery)
print ("EKF OK?: ", vehicle.ekf_ok)
print ("Last Heartbeat: ", vehicle.last_heartbeat)
print ("Rangefinder: ", vehicle.rangefinder)
print ("Rangefinder distance: ", vehicle.rangefinder.distance)
print ("Rangefinder voltage: ", vehicle.rangefinder.voltage)
print ("Heading: ", vehicle.heading)
print ("Is Armable?: ", vehicle.is_armable)
print ("System status: ", vehicle.system_status.state)
print ("Mode: ", vehicle.mode.name)    # settable
print ("Armed: ",  vehicle.armed)    # settable
