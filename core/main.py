import cv2
from core.ai_engine import AIEngine

#kamera gelene kadar

def main():
    #videocapture 0 (integrated cam)
    cap = cv2.VideoCapture(0)
    ai = AIEngine("yolov8n.pt") 

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        annotated_frame, boxes = ai.process_frame(frame)
        
        cv2.imshow("YOLOv8 & ByteTrack Test", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
