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

