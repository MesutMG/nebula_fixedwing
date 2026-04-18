from pymavlink import mavutil

port = 'udp:127.0.0.1:14550'
the_connection = mavutil.mavlink_connection(port)

# Wait for the first heartbeat
#   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

# Once connected, use 'the_connection' to get and send messages


while True:
    msg = the_connection.recv_match(type="ATTITUDE", blocking=True)
    print(msg)
