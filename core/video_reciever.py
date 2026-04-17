import cv2

#openIPC ip'si bu olacak
#rtsp://IP_ADRESS:8554/stream0
stream_url = "rtsp://127.0.0.1:14550/stream0"
#kamera geldikten sonra test et 192.168.1.xxx olacak

cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Görüntü akışına bağlanılamadı!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow("openIPC live", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
