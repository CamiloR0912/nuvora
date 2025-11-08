import os
import cv2

index = int(os.getenv("CAM_INDEX", "0"))  # cambia a tu índice si es necesario
cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # CAP_DSHOW ayuda en Windows

if not cap.isOpened():
    raise RuntimeError(f"No se pudo abrir la cámara con índice {index}")

print(f"✅ Cámara abierta en índice {index}. Presiona 'q' para salir.")

while True:
    ok, frame = cap.read()
    if not ok:
        print("⚠️ No se pudo leer frame. Verifica permisos/índice.")
        break
    cv2.imshow("Stream de prueba", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()