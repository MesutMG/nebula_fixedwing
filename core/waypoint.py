import time
from pymavlink import mavutil, mavwp

def arm(conn):
    conn.mav.command_long_send(conn.target_system, conn.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    print("armed")

def disarm(conn):
    conn.mav.command_long_send(conn.target_system, conn.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
    print("disarmed")

def set_mode_take_off(conn):
    conn.set_mode(13)
    print("take off mode")
    time.sleep(1)

def takeoff(conn, alt):
    conn.mav.command_long_send(conn.target_system, conn.target_component, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 15, 0, 0, 0, 0, 0, alt)
    print("taking off")
    for i in range(3):
        conn.wait_heartbeat()
        time.sleep(1)

def set_mode_guided(conn):
    conn.set_mode(15)
    print("guided mode")
    time.sleep(1)


def get_alt():
    msg = conn.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
    
    while True:
        m = conn.recv_match(type="GLOBAL_POSITION_INT", blocking=False)
        if not m:
            break
        msg = m
    return msg.relative_alt / 1000.0

def add_mission_waypoint(line):
    index = int(line[0])
    enlem = float(line[8])
    boylam = float(line[9])
    alt = int(float(line[10]))
    waypoints.add(mavutil.mavlink.MAVLink_mission_item_message(
        conn.target_system, conn.target_component, index,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        0, 0, 0, 0, 0, 0, enlem, boylam, alt))

def add_mission_loiter(line):
    index = int(line[0])
    loiter_turns = float(line[4])
    radius = float(line[6])
    exitmode = int(float(line[7]))
    enlem = float(line[8])
    boylam = float(line[9])
    alt = int(float(line[10]))
    print(index,loiter_turns,radius,enlem,boylam)
    waypoints.add(mavutil.mavlink.MAVLink_mission_item_message(
        conn.target_system, conn.target_component, index,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_LOITER_TURNS,
        0, 1, loiter_turns, exitmode, radius, 0, enlem, boylam, alt))

def upload_missions():
    conn.waypoint_clear_all_send()
    conn.waypoint_count_send(waypoints.count())
    for i in range(waypoints.count()):
        msg = conn.recv_match(type=["MISSION_REQUEST"], blocking=True)
        conn.mav.send(waypoints.wp(msg.seq))
        print(f"Sending waypoint {msg.seq}")

def add_missions():
    with open("/home/mesut/projects/ihaproject/core/waypoints.waypoints", "r") as f:

        #skips first line
        line = f.readline()
        while line:
            line = f.readline().split()

            #not proper 12 element waypoint txt
            if len(line) < 11:
                print("not proper 12 element waypoints")
                break
            
            match line[3]:
                case "16":
                    add_mission_waypoint(line)
                case "18":
                    add_mission_loiter(line)


if __name__ == '__main__':
    ip = 'udp:127.0.0.1:14550' 
    conn = mavutil.mavlink_connection(ip, baud=115200, autoreconnect=True)
    conn.wait_heartbeat()
    print("baglandi")
    
    waypoints = mavwp.MAVWPLoader()
    
    #waypointleri uploading
    #send_waypoints(conn, waypoints)
    
    arm(conn)

    set_mode_take_off(conn)

    arm(conn)

    takeoff(conn, 50)
    
    print("kalkiyor, 2 saniye bekleniyor...")
    for _ in range(2):
        conn.wait_heartbeat()
        time.sleep(1)

    set_mode_guided(conn)
    
    add_missions()

    upload_missions()
    
    mode_id = conn.mode_mapping()['AUTO']
    conn.set_mode(mode_id)
    print("autoya gelildi, waypoint izleniyor")