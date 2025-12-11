"""
Particle System untuk Blink Beat — Visualisasi Partikel Real-time

Modul ini menghasilkan efek partikel yang muncul di sekitar mata saat berkedip.
Menggunakan rendering OpenCV native untuk performa optimal.

Fitur:
- Partikel berwarna sesuai jenis kedipan (biru, merah, emas)
- Arah emisi berdasarkan posisi mata
- Fade out transparan otomatis
- Garbage collection partikel mati
"""

import cv2
import numpy as np
from collections import deque

class Particle:
    """
    Representasi partikel tunggal dengan fisika sederhana.
    
    Atribut:
        x, y (float): Posisi partikel
        vx, vy (float): Kecepatan partikel
        life (int): Durasi hidup (frame)
        color (tuple): Warna partikel dalam format BGR
    """
    
    def __init__(self, x, y, color, direction="random"):
        """
        Inisialisasi partikel dengan posisi, warna, dan arah.
        
        Args:
            x, y (float): Posisi awal partikel
            color (tuple): Warna dalam format BGR (blue, green, red)
            direction (str): Arah emisi - "left", "right", "burst", atau "random"
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.life = 100  # durasi hidup (frame)
        self.color = color  # BGR tuple
        
        # Arah partikel berdasarkan lokasi mata
        if direction == "left":
            self.vx = np.random.uniform(-3, -1)
            self.vy = np.random.uniform(-2, 2)
        elif direction == "right":
            self.vx = np.random.uniform(1, 3)
            self.vy = np.random.uniform(-2, 2)
        elif direction == "burst":
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(2, 4)
            self.vx = np.cos(angle) * speed
            self.vy = np.sin(angle) * speed
        else:  # random
            self.vx = np.random.uniform(-2, 2)
            self.vy = np.random.uniform(-2, 2)

    def update(self):
        """Update posisi dan durasi hidup partikel."""
        self.x += self.vx
        self.y += self.vy
        self.life -= 2  # mati lebih cepat → efek lebih dinamis

    def draw(self, frame):
        """Gambar partikel ke frame dengan efek transparan."""
        if self.life > 0:
            alpha = min(1.0, self.life / 100)
            radius = int(3 * alpha)
            if radius > 0:
                # Gambar lingkaran transparan (simulasi via blending)
                overlay = frame.copy()
                cv2.circle(overlay, (int(self.x), int(self.y)), radius, self.color, -1)
                cv2.addWeighted(overlay, 0.6 * alpha, frame, 1 - 0.6 * alpha, 0, frame)
                return True
        return False


class ParticleSystem:
    """
    Sistem manajemen partikel untuk Blink Beat.
    
    Atribut:
        particles (deque): Kumpulan partikel aktif
    """
    
    def __init__(self):
        """Inisialisasi sistem partikel kosong."""
        self.particles = deque(maxlen=500)  # batas maksimal partikel
    
    def emit(self, x, y, color, count=20, direction="random"):
        """
        Emisi partikel dari titik (x, y).
        
        Args:
            x, y (int): Koordinat titik emisi
            color (tuple): Warna partikel dalam format BGR
            count (int): Jumlah partikel yang diemisi
            direction (str): Arah emisi - "left", "right", "burst", atau "random"
        """
        for _ in range(count):
            self.particles.append(Particle(x, y, color, direction))
    
    def update_and_draw(self, frame):
        """
        Update posisi semua partikel dan gambar ke frame.
        
        Args:
            frame (numpy.ndarray): Frame tempat partikel akan digambar
        """
        # Hapus partikel mati saat update
        alive = []
        for p in self.particles:
            p.update()
            if p.draw(frame):
                alive.append(p)
        self.particles = deque(alive, maxlen=500)
    
    def clear(self):
        """Hapus semua partikel."""
        self.particles.clear()