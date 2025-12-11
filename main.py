"""
Blink Beat — Drum Interaktif dengan Kedipan Mata
Author: Hayyatul Fajri & Muhammad Fasya Atthoriq
"""

import sys
import os
import cv2

# Setup path untuk import dari folder src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from blink_detector import BlinkDetector
from audio_manager import DrumAudio
from particle_system import ParticleSystem

def main():
    """Fungsi utama program Blink Beat."""
    print("🚀 Blink Beat v2.0 — Drum dengan Kedipan Mata!")
    print("✨ Visualisasi partikel real-time + suara drum")
    print("👉 Tekan 'q' pada keyboard untuk keluar")
    print("-" * 50)
    
    # Inisialisasi komponen
    try:
        detector = BlinkDetector()
        audio = DrumAudio()
        particles = ParticleSystem()
    except Exception as e:
        print(f"❌ Error saat inisialisasi: {e}")
        return
    
    # Buka webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Gagal membuka webcam. Pastikan kamera terhubung dan tidak digunakan aplikasi lain.")
        detector.release()
        audio.cleanup()
        return
    
    # Optimalkan webcam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # matikan autofocus
    cap.set(cv2.CAP_PROP_FOCUS, 250)    # fokus manual
    
    print("📷 Webcam berhasil dibuka. Tunggu kalibrasi...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Gagal membaca frame dari webcam")
                break
            
            # Balik frame horizontal agar natural
            frame = cv2.flip(frame, 1)
            
            # Deteksi kedipan + dapatkan posisi mata
            frame, left_blink, right_blink, both_blink, left_pos, right_pos = detector.detect_blinks(frame)
            
            # Trigger audio & partikel
            if left_blink:
                audio.play("snare")
                particles.emit(left_pos[0], left_pos[1], (255, 100, 0), 30, "left")  # biru
            
            if right_blink:
                audio.play("kick")
                particles.emit(right_pos[0], right_pos[1], (0, 100, 255), 30, "right")  # merah
            
            if both_blink:
                audio.play("cymbal")
                # Rata-rata posisi kedua mata
                cx = (left_pos[0] + right_pos[0]) // 2
                cy = (left_pos[1] + right_pos[1]) // 2
                particles.emit(cx, cy, (0, 215, 255), 50, "burst")  # emas
            
            # Update & gambar partikel
            particles.update_and_draw(frame)
            
            # Tampilkan frame
            cv2.imshow('Blink Beat — Drum + Partikel', frame)
            
            # Keluar jika tombol 'q' ditekan
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("👋 Program dihentikan oleh pengguna.")
                break
    
    finally:
        # Cleanup resource (pastikan selalu dijalankan)
        print("🧹 Membersihkan resource...")
        cap.release()
        cv2.destroyAllWindows()
        detector.release()
        audio.cleanup()
        print("✅ Program Blink Beat selesai. Terima kasih!")

if __name__ == "__main__":
    main()