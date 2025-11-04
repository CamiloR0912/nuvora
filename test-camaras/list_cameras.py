import cv2

print("🔍 Buscando cámaras disponibles...")
for i in range(10):  # prueba los primeros 10 índices
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Cámara encontrada en índice {i}")
        cap.release()
    else:
        print(f"❌ No se detecta cámara en índice {i}")
