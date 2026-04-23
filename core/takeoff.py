import time
from pymavlink import mavutil

port = 'udp:127.0.0.1:14550'
the_connection = mavutil.mavlink_connection(port)

# Wait for the first heartbeat
#   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

#!!!
# Once connected, use 'the_connection' to get and send messages
#!!!

#arming
#usage bits: [0, ON/OFF, 0, 0, 0, 0, 0, 0]
the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

msg = the_connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)
#0: ok
#mavlink.io/en/messages/common.html#MAV_RESULT


#set guided mode
#the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, mavutil.mavlink.MAV_CMD_DO_SET_MODE, 8, 0, 0, 0, 0, 0, 0, 0)
the_connection.set_mode(13)
time.sleep(1)
msg = the_connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)

the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
msg = the_connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)

#takeoff
the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 15, 0, 0, 0, 0, 0, 40)
msg = the_connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)
for i in range(10):
    the_connection.wait_heartbeat()
    time.sleep(1)

the_connection.set_mode(15)

type_mask = 3576
the_connection.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
                        10, the_connection.target_system, the_connection.target_component,
                        mavutil.mavlink.MAV_FRAME_LOCAL_NED, type_mask, 100, 50, -40, 0, 0, 0, 0, 0, 0, 0, 0))
msg = the_connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)
print("naved")
