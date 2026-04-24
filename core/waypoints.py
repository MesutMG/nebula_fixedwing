import time
from pymavlink import mavutil, mavwp
"""
def send_waypoints(conn, wps):
    conn.mav.mission_clear_all_send(conn.target_system, conn.target_component)
    print("Clearing old missions: ", conn.recv_match(type='MISSION_ACK', blocking=True))

    '''https://mavlink.io/en/messages/common.html#MISSION_COUNT
    This message is emitted as response to MISSION_REQUEST_LIST by the MAV and
    to initiate a write transaction. The GCS can then request the individual mission
    item based on the knowledge of the total number of waypoints.'''
    conn.mav.mission_count_send(conn.target_system, conn.target_component, len(wps))

    for i in range(len(wps)):
        print("Sending the mission count: ",conn.recv_match(type=['MISSION_REQUEST', 'MISSION_REQUEST_INT'], blocking=True))
        wp = wps[i]

        '''https://mavlink.io/en/messages/common.html#MISSION_ITEM_INT
        Message encoding a mission item. This message is emitted to announce the presence
        of a mission item and to set a mission item on the system. The mission item can be
        either in x, y, z meters (type: LOCAL) or x:lat, y:lon, z:altitude. Local frame is
        Z-down, right handed (NED), global frame is Z-up, right handed (ENU). NaN or
        INT32_MAX may be used in float/integer params (respectively) to indicate
        optional/default values (e.g. to use the component's current latitude, yaw rather
        than a specific value).'''
        conn.mav.mission_item_int_send(
            conn.target_system,
            conn.target_component,
            i,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0, 1,
            0, 1, 0, 0,
            int(wp['x'] * 1e7),
            int(wp['y'] * 1e7),
            wp['z']
        )
        
    print(conn.recv_match(type='MISSION_ACK', blocking=True))
"""




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

'''def takeoff(alt):
    conn.mav.command_long_send(conn.target_system, conn.target_component,
                                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                0, 0, 0, 0 ,0, 0 ,0, alt)
    
    while get_alt() < alt:
        print(f"Irtifa: {get_alt()}\tHedef: {alt}")
    print(f"Hedef irtifaya ulasildi: {get_alt()}")'''


def add_mission(index, enlem, boylam, alt):
    waypoints.add(mavutil.mavlink.MAVLink_mission_item_message(
        conn.target_system, conn.target_component, index,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        0, 0, 0, 0, 0, 0, enlem, boylam, alt))
    
def upload_missions():
    conn.waypoint_clear_all_send()
    conn.waypoint_count_send(waypoints.count())
    for i in range(waypoints.count()):
        msg = conn.recv_match(type=["MISSION_REQUEST"], blocking=True)
        conn.mav.send(waypoints.wp(msg.seq))
        print(f"Sending waypoint {msg.seq}")

def add_missions():
    with open("waypoints.waypoints", "r") as f:

        #skips first line
        line = f.readline()
        while line:
            line = f.readline().split()
            if len(line) >= 11:
                add_mission(int(line[0]), float(line[8]), float(line[9]), 100)
                print(int(line[0]), float(line[8]), float(line[9]), 100)



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