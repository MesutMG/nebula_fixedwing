import cv2
from ultralytics import YOLO

class AIEngine:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def process_frame(self, frame):
        #byte-track ile nesne takibi, persist=true surekli donmesini sagliyor
        results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)
        
        #tespit edilen kutular ve takip IDdleri
        annotated_frame = results[0].plot()
        
        #kordinat ve ID
        return annotated_frame, results[0].boxes
