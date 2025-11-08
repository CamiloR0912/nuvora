import cv2

def generate_mjpeg(manager, cam_id: str):
    """Genera un stream MJPEG continuo para la cámara seleccionada.

    Usa la misma instancia de CameraManager que administra las cámaras
    en la aplicación principal para evitar cámaras "no registradas".
    """
    while True:
        try:
            frame = manager.get_frame(cam_id)
            ok, buffer = cv2.imencode('.jpg', frame)
            if not ok:
                # Si la codificación falla, intenta el siguiente frame
                continue
            frame_bytes = buffer.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )
        except Exception:
            # Corta el stream ante errores (por ejemplo, cámara desconectada)
            break
