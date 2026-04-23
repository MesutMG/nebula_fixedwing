import time
from pymavlink import mavutil

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

if __name__ == '__main__':
    ip = 'udp:127.0.0.1:14550' 
    conn = mavutil.mavlink_connection(ip)
    conn.wait_heartbeat()
    
    waypoints = [
        {'x': 40.899067, 'y': 29.158529, 'z': 30}, # WP 0 (home)
        {'x': 40.899500, 'y': 29.158529, 'z': 30}, # WP 1 (kuzet)
        {'x': 40.899500, 'y': 29.159000, 'z': 30}, # WP 2 (dogu)
        {'x': 40.899067, 'y': 29.159000, 'z': 30}, # WP 3 (guney)
        {'x': 40.899067, 'y': 29.158529, 'z': 30}  # WP 4 (home)
    ]
    
    #waypointleri uploading
    send_waypoints(conn, waypoints)
    
    #takeoff
    conn.set_mode(conn.mode_mapping().get('GUIDED', 4))
    conn.mav.command_long_send(conn.target_system, conn.target_component,
                               mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                               0, 1, 0, 0, 0, 0, 0, 0)
    print("Armed: ", conn.recv_match(type="COMMAND_ACK", blocking=True))
    
    print("kalkiyor, 5 saniye bekleniyor...")
    for _ in range(5):
        conn.wait_heartbeat()
        time.sleep(1)
    
    mode_id = conn.mode_mapping()['AUTO']
    conn.set_mode(mode_id)
    print("autoya gelildi, waypoint izleniyor")