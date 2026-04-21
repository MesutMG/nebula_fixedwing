from pymavlink import mavutil

def send_waypoint(conn, noktalar):
    conn.mav.mission_clear_all_send(conn.target_system, conn.target_component)
    print(conn.recv_match(type='MISSION_ACK', blocking=True))

    conn.mav.mission_count_send(conn.target_system, conn.target_component, len(noktalar))

    for seq, wp in enumerate(noktalar):
        print(conn.recv_match(type=['MISSION_REQUEST', 'MISSION_REQUEST_INT'], blocking=True))
        
        conn.mav.mission_item_int_send(
            conn.target_system, 
            conn.target_component, 
            seq,                                               
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, 
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,              
            0, 1, 0, 0, 0, 0,                                  
            int(wp['enlem'] * 1e7), 
            int(wp['boylam'] * 1e7), 
            wp['irtifa']
        )
        
    print(conn.recv_match(type='MISSION_ACK', blocking=True))


if __name__ == '__main__':
    ip = 'udp:127.0.0.1:14550' 
    conn = mavutil.mavlink_connection(ip)
    conn.wait_heartbeat()
    
    waypoints = [
        {'enlem': -35.358000, 'boylam': 149.170000, 'irtifa': 50.0},
        {'enlem': -35.368000, 'boylam': 149.160000, 'irtifa': 50.0},
        {'enlem': -35.368000, 'boylam': 149.170000, 'irtifa': 50.0},
        {'enlem': -35.358000, 'boylam': 149.160000, 'irtifa': 50.0},
        {'enlem': -35.358000, 'boylam': 149.170000, 'irtifa': 50.0}
    ]
    
    send_waypoint(conn, waypoints)
    mode_id = master.mode_mapping()['AUTO']
    conn.set_mode(mode_id)