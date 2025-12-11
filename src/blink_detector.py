"""
Blink Detector untuk Blink Beat — Deteksi Kedipan Mata Real-time

Modul ini mendeteksi kedipan mata menggunakan MediaPipe Face Mesh dan
menghitung Eye Aspect Ratio (EAR) untuk menentukan apakah mata terbuka atau tertutup.

Fitur:
- Deteksi wajah real-time dengan MediaPipe
- Kalibrasi otomatis threshold EAR
- Deteksi kedipan kiri, kanan, dan ganda
- Return posisi mata untuk visualisasi partikel
- Anti-noise dengan konfirmasi frame dan cooldown
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

class BlinkDetector:
    """
    Kelas utama untuk deteksi kedipan mata menggunakan MediaPipe Face Mesh.
    
    Atribut:
        face_mesh: Instance MediaPipe FaceMesh
        LEFT_EYE: Indeks landmark untuk mata kiri
        RIGHT_EYE: Indeks landmark untuk mata kanan
        ear_threshold: Threshold EAR untuk deteksi kedipan
        calibrated: Status kalibrasi otomatis
    """
    
    def __init__(self):
        """
        Inisialisasi detector dengan parameter optimal untuk berbagai kondisi kamera.
        """
        # Inisialisasi MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4
        )
        
        # Landmark mata (6 titik per mata)
        self.LEFT_EYE = [33, 133, 160, 159, 158, 144]   # [kiri, kanan, atas-luar, atas-dalam, bawah-dalam, bawah-luar]
        self.RIGHT_EYE = [263, 362, 387, 385, 384, 390] # [kiri, kanan, atas-luar, atas-dalam, bawah-dalam, bawah-luar]
        
        # Kalibrasi otomatis
        self.ear_buffer = deque(maxlen=30)  # buffer 30 frame terakhir untuk kalibrasi
        self.ear_threshold = 0.25            # nilai awal — akan disesuaikan otomatis
        self.calibrated = False
        
        # Parameter deteksi
        self.BLINK_COOLDOWN = 0.25           # 250ms antar kedip
        self.CONFIRM_FRAMES = 2              # butuh 2 frame berturut-turut untuk validasi
        
        # State tracking
        self.left_counter = 0
        self.right_counter = 0
        self.both_counter = 0
        self.last_blink_time = 0
        
        # FPS tracking
        self.prev_time = time.time()
        self.fps = 0

    def _euclidean_dist(self, a, b):
        """
        Hitung jarak Euclidean antara dua titik.
        
        Args:
            a (tuple): Koordinat titik pertama (x, y)
            b (tuple): Koordinat titik kedua (x, y)
            
        Returns:
            float: Jarak Euclidean
        """
        return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def _calculate_ear_from_points(self, eye_points):
        """
        Hitung EAR dari koordinat pixel (6 titik).
        
        Args:
            eye_points (list): List 6 koordinat (x, y) dari landmark mata
            
        Returns:
            float: Nilai EAR (0.0 - 1.0)
        """
        if len(eye_points) < 6:
            return 0.0
        
        # Hitung jarak vertikal (2 pasang)
        A = self._euclidean_dist(eye_points[1], eye_points[5])
        B = self._euclidean_dist(eye_points[2], eye_points[4])
        
        # Hitung jarak horizontal
        C = self._euclidean_dist(eye_points[0], eye_points[3])
        
        # Hitung EAR (hindari pembagian dengan nol)
        if C == 0:
            return 0.0
        
        ear = (A + B) / (2.0 * C)
        return ear

    def detect_blinks(self, frame):
        """
        Deteksi kedipan dan kembalikan posisi mata untuk partikel.
        
        Args:
            frame (numpy.ndarray): Frame input dari webcam
            
        Returns:
            tuple: (frame_output, left_blink, right_blink, both_blink, left_eye_pos, right_eye_pos)
                - frame_output: Frame dengan visualisasi deteksi
                - left_blink: Boolean, True jika mata kiri berkedip
                - right_blink: Boolean, True jika mata kanan berkedip
                - both_blink: Boolean, True jika kedua mata berkedip
                - left_eye_pos: (x, y) koordinat pusat mata kiri
                - right_eye_pos: (x, y) koordinat pusat mata kanan
        """
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        left_blink = right_blink = both_blink = False
        left_eye_center = (w // 3, h // 2)      # default fallback
        right_eye_center = (2 * w // 3, h // 2) # default fallback
        
        current_time = time.time()
        
        # 🔥 INISIALISASI DEFAULT UNTUK EAR (FIX: UnboundLocalError)
        left_ear = 0.0
        right_ear = 0.0
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Hitung posisi pusat mata kiri & kanan
                left_x = sum(int(face_landmarks.landmark[i].x * w) for i in self.LEFT_EYE) // len(self.LEFT_EYE)
                left_y = sum(int(face_landmarks.landmark[i].y * h) for i in self.LEFT_EYE) // len(self.LEFT_EYE)
                right_x = sum(int(face_landmarks.landmark[i].x * w) for i in self.RIGHT_EYE) // len(self.RIGHT_EYE)
                right_y = sum(int(face_landmarks.landmark[i].y * h) for i in self.RIGHT_EYE) // len(self.RIGHT_EYE)
                
                left_eye_center = (left_x, left_y)
                right_eye_center = (right_x, right_y)
                
                # Hitung EAR
                left_eye_points = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in self.LEFT_EYE]
                right_eye_points = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in self.RIGHT_EYE]
                
                left_ear = self._calculate_ear_from_points(left_eye_points)
                right_ear = self._calculate_ear_from_points(right_eye_points)
                
                # Kalibrasi otomatis (30 frame)
                if not self.calibrated:
                    self.ear_buffer.append((left_ear, right_ear))
                    if len(self.ear_buffer) == 30:
                        left_vals = sorted([x[0] for x in self.ear_buffer], reverse=True)[:22]
                        right_vals = sorted([x[1] for x in self.ear_buffer], reverse=True)[:22]
                        open_left = np.mean(left_vals)
                        open_right = np.mean(right_vals)
                        self.ear_threshold = 0.65 * min(open_left, open_right)
                        self.calibrated = True
                        print(f"✅ Kalibrasi selesai! EAR Threshold: {self.ear_threshold:.3f}")
                
                thresh = self.ear_threshold if self.calibrated else 0.22
                
                # Deteksi kedipan (2 frame konfirmasi)
                if left_ear < thresh:
                    self.left_counter += 1
                else:
                    if self.left_counter >= self.CONFIRM_FRAMES and (current_time - self.last_blink_time) > self.BLINK_COOLDOWN:
                        left_blink = True
                        self.last_blink_time = current_time
                    self.left_counter = 0
                
                if right_ear < thresh:
                    self.right_counter += 1
                else:
                    if self.right_counter >= self.CONFIRM_FRAMES and (current_time - self.last_blink_time) > self.BLINK_COOLDOWN:
                        right_blink = True
                        self.last_blink_time = current_time
                    self.right_counter = 0
                
                if left_ear < thresh and right_ear < thresh:
                    self.both_counter += 1
                else:
                    if self.both_counter >= self.CONFIRM_FRAMES and (current_time - self.last_blink_time) > self.BLINK_COOLDOWN:
                        both_blink = True
                        self.last_blink_time = current_time
                    self.both_counter = 0
        
        # Update FPS
        curr_time = time.time()
        if curr_time - self.prev_time > 0:  # hindari pembagian dengan nol
            self.fps = 1 / (curr_time - self.prev_time)
        else:
            self.fps = 0
        self.prev_time = curr_time
        
        # Tampilkan info di frame
        status = "Kalibrasi..." if not self.calibrated else f"Thresh: {self.ear_threshold:.2f}"
        cv2.putText(frame, f'EAR L: {left_ear:.2f} R: {right_ear:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        cv2.putText(frame, f'FPS: {int(self.fps)} {status}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
        
        # Tampilkan teks kedipan
        if left_blink: 
            cv2.putText(frame, '🥁 SNARE!', (w//2-80, h//2-50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 200, 0), 2)
        if right_blink: 
            cv2.putText(frame, '🥁 KICK!', (w//2-70, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 255), 2)
        if both_blink: 
            cv2.putText(frame, '🥁 CYMBAL!', (w//2-90, h//2+50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        return frame, left_blink, right_blink, both_blink, left_eye_center, right_eye_center

    def release(self):
        """
        Bersihkan resource Face Mesh.
        Harus dipanggil sebelum program berakhir.
        """
        self.face_mesh.close()
        print("👋 Face Mesh resource dibersihkan.")