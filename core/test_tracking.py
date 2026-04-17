import cv2
from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    print("Sistem çalışıyor... Çıkmak için 'q' tuşuna basın.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy() #kutu koordinatları [x1, y1, x2, y2]
            track_ids = results[0].boxes.id.int().cpu().numpy() #IDler
            
        annotated_frame = results[0].plot()

        cv2.imshow("YOLOv8 + Byte-Track Hedef Takibi", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
