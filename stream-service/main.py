from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from camera_manager import CameraManager
from stream_generator import generate_mjpeg
import os
import cv2

app = FastAPI(title="Camera Service", version="1.0")

# Habilitar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

camera_manager = CameraManager()

@app.on_event("startup")
def startup_event():
    # Puedes registrar cámaras aquí automáticamente
    # 0 = webcam local, o una URL RTSP / IP
    try:
        cam_index = int(os.getenv("CAM_INDEX", "0"))
        camera_manager.add_camera("entrada", cam_index)
        # camera_manager.add_camera("salida", "rtsp://usuario:clave@192.168.1.10/stream")
    except Exception as e:
        print(f"⚠️ Error al iniciar cámara: {e}")

@app.get("/cameras")
def list_cameras():
    """Lista las cámaras registradas."""
    return {"cameras": list(camera_manager.cameras.keys())}

@app.get("/cameras/{cam_id}/snapshot")
def get_snapshot(cam_id: str):
    """Devuelve una imagen puntual de la cámara."""
    try:
        frame = camera_manager.get_frame(cam_id)
        _, buffer = cv2.imencode(".jpg", frame)
        return Response(content=buffer.tobytes(), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/cameras/{cam_id}/stream")
def get_stream(cam_id: str):
    """Devuelve un stream MJPEG continuo."""
    if cam_id not in camera_manager.cameras:
        raise HTTPException(status_code=404, detail="Cámara no registrada")
    return StreamingResponse(generate_mjpeg(camera_manager, cam_id),
                             media_type="multipart/x-mixed-replace; boundary=frame")

@app.on_event("shutdown")
def shutdown_event():
    camera_manager.release()
