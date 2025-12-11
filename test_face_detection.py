import cv2
import mediapipe as mp
import time

# Inisialisasi MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Inisialisasi drawing utility
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Buka webcam
cap = cv2.VideoCapture(0)

print("Tekan tombol 'q' pada keyboard untuk keluar")
print("Sedang mendeteksi wajah...")

while True:
    # Baca frame dari webcam
    success, image = cap.read()
    if not success:
        print("Gagal mengakses webcam")
        break
    
    # Konversi warna dari BGR (OpenCV default) ke RGB (yang dibutuhkan MediaPipe)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Proses deteksi wajah
    results = face_mesh.process(image_rgb)
    
    # Jika wajah terdeteksi
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Gambar titik-titik wajah
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec
            )
    
    # Tampilkan hasil
    cv2.imshow('Face Detection Test - Tekan q untuk keluar', image)
    
    # Keluar jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan resource
cap.release()
cv2.destroyAllWindows()
face_mesh.close()
print("Program selesai. Webcam ditutup.")