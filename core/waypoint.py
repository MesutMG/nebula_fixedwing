from pymavlink import mavutil

def waypoint_yukle(master, noktalar):
    # 1. Mevcut görevi temizle
    master.mav.mission_clear_all_send(master.target_system, master.target_component)
    master.recv_match(type='MISSION_ACK', blocking=True)

    # 2. Toplam waypoint sayısını bildir
    master.mav.mission_count_send(master.target_system, master.target_component, len(noktalar))

    # 3. Noktaları sırayla gönder
    for seq, wp in enumerate(noktalar):
        # İHA'dan o anki sıra için istek bekle
        msg = master.recv_match(type=['MISSION_REQUEST', 'MISSION_REQUEST_INT'], blocking=True)
        
        # MAV_CMD_NAV_WAYPOINT komutu ile koordinatı gönder
        master.mav.mission_item_int_send(
            master.target_system, 
            master.target_component, 
            seq,                                               # Sıra no
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # Referans: Kalkış noktası
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,              # Komut: Waypoint'e git
            0, 1, 0, 0, 0, 0,                                  # Diğer parametreler (gecikme, kabul yarıçapı vb.)
            int(wp['enlem'] * 1e7), 
            int(wp['boylam'] * 1e7), 
            wp['irtifa']
        )
        
    # 4. Yükleme tamamlandı onayını (MISSION_ACK) bekle
    master.recv_match(type='MISSION_ACK', blocking=True)
    print("Tüm görev noktaları uçağa yüklendi.")

if __name__ == '__main__':
    baglanti_adresi = 'udp:127.0.0.1:14550' 
    master = mavutil.mavlink_connection(baglanti_adresi)
    master.wait_heartbeat()
    
    # Yüklenecek hedef noktalar
    gorev_noktalari = [
        {'enlem': -35.155137, 'boylam': 148.369530, 'irtifa': 30.0}, # Waypoint 0 (Genellikle HOME kabul edilir)
        {'enlem': -36.155500, 'boylam': 149.370000, 'irtifa': 40.0}, # Waypoint 1
        {'enlem': -33.156000, 'boylam': 150.370500, 'irtifa': 40.0}  # Waypoint 2
    ]
    
    waypoint_yukle(master, gorev_noktalari)



def gorevi_baslat(master):
    # AUTO modunun ID'sini al (ArduPlane için genellikle 10, ArduCopter için 3'tür)
    # mode_mapping() ile dinamik olarak bulmak en güvenlisidir.
    mode = 'AUTO'
    mode_id = master.mode_mapping()[mode]
    
    master.set_mode(mode_id)
    print(f"Uçuş modu {mode} olarak ayarlandı. Görev başlıyor...")

if __name__ == '__main__':
    baglanti_adresi = 'udp:127.0.0.1:14550' 
    master = mavutil.mavlink_connection(baglanti_adresi)
    
    master.wait_heartbeat()
    print("İHA bağlantısı başarılı!")
    
    gorevi_baslat(master)
