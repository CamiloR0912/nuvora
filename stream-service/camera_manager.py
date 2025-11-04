import cv2
from threading import Lock

class CameraManager:
    def __init__(self):
        self.cameras = {}
        self.locks = {}

    def add_camera(self, cam_id, source):
        """Agrega o reinicia una cámara (puede ser 0, 1 o una URL RTSP/HTTP)."""
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir la cámara {source}")
        self.cameras[cam_id] = cap
        self.locks[cam_id] = Lock()

    def get_frame(self, cam_id):
        """Obtiene un frame actual de la cámara."""
        if cam_id not in self.cameras:
            raise ValueError(f"Cámara {cam_id} no registrada.")
        cap = self.cameras[cam_id]
        with self.locks[cam_id]:
            ret, frame = cap.read()
        if not ret:
            raise ValueError(f"No se pudo leer frame de cámara {cam_id}")
        return frame

    def release(self):
        """Cierra todas las cámaras."""
        for cap in self.cameras.values():
            cap.release()
