import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time


ip = 'udp:127.0.0.1:14550'
vehicle = connect(ip, wait_ready=True)

if vehicle:
   print("baglandi")

   if not vehicle.armed:
        print("Uçak Arm ediliyor...")
        vehicle.armed = True
        while not vehicle.armed:
            time.sleep(1)
        print("Arm edildi.")

def goto(enlem, boylam, irtifa):
    if vehicle.mode.name != "GUIDED":
        vehicle.mode = VehicleMode("GUIDED")
        print("guided")
        while not vehicle.mode.name == 'GUIDED':
            time.sleep(1)
            
    if not vehicle.armed:
        vehicle.armed = True
        while not vehicle.armed:
            print("Arm edilmesi bekleniyor...")
            time.sleep(1)
            
    hedef_konum = LocationGlobalRelative(enlem, boylam, irtifa)
    
    vehicle.simple_goto(hedef_konum)
    print(f"hedefe gidiyor...\nenlem: {enlem},\nboylam: {boylam},\nirtifa: {irtifa}\n")

goto(-35.015137, 149.979530, 10)

while True:
    print(f"Mevcut İrtifa: {vehicle.location.global_relative_frame.alt}")
    print(f"Mevcut Konim: {vehicle.location.global_frame}")
    time.sleep(2)
