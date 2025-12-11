"""
Audio Manager untuk Blink Beat — Drum Interaktif dengan Kedipan Mata

Modul ini mengelola pemutaran suara drum secara real-time berdasarkan input visual
(kedipan mata). Menggunakan pygame.mixer untuk playback dengan latensi rendah.

Fitur:
- Load 3 suara: snare, kick, cymbal dari direktori assets/sounds/
- Playback non-blocking (tidak menghentikan loop utama)
- Resource cleanup otomatis
- Error handling untuk file tidak ditemukan

Lisensi: CC0 — seluruh suara di-generate atau diunduh dari sumber bebas hak cipta
"""

import pygame
import os
from typing import Optional


class DrumAudio:
    """
    Manajer audio untuk memicu suara drum saat deteksi kedipan.

    Atribut:
        sounds (dict): Dictionary berisi objek pygame.mixer.Sound:
            - "snare": suara snare drum
            - "kick": suara bass drum
            - "cymbal": suara cymbal crash
    """

    def __init__(self):
        """
        Inisialisasi mixer pygame dan muat file suara dari assets/sounds/.
        
        Raises:
            FileNotFoundError: Jika salah satu file suara tidak ditemukan.
            pygame.error: Jika mixer gagal diinisialisasi.
        """
        # Inisialisasi pygame mixer dengan setting optimal untuk real-time
        # buffer=512 → latensi ~12ms pada 44.1kHz (cukup responsif untuk kedipan)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Tentukan path ke folder suara (relatif terhadap file ini)
        base_dir = os.path.dirname(__file__)
        sound_dir = os.path.join(base_dir, "..", "assets", "sounds")
        
        # Daftar suara yang dibutuhkan
        sound_files = {
            "snare": "snare.wav",
            "kick": "kick.wav",
            "cymbal": "cymbal.wav"
        }
        
        self.sounds = {}
        
        # Muat setiap suara
        for name, filename in sound_files.items():
            filepath = os.path.join(sound_dir, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(
                    f"File suara '{filename}' tidak ditemukan di: {filepath}\n"
                    "Pastikan struktur folder: assets/sounds/{snare,kick,cymbal}.wav"
                )
            
            try:
                self.sounds[name] = pygame.mixer.Sound(filepath)
                print(f"✅ Suara '{name}' dimuat dari: {filename}")
            except pygame.error as e:
                raise RuntimeError(f"Gagal memuat suara '{name}' dari {filename}: {e}")
        
        print("🔊 DrumAudio siap — 3 suara berhasil dimuat.")

    def play(self, sound_type: str) -> bool:
        """
        Memainkan suara drum sesuai tipe yang diminta.

        Args:
            sound_type (str): Tipe suara yang ingin dimainkan.
                Nilai yang valid: "snare", "kick", "cymbal"

        Returns:
            bool: True jika suara berhasil dipicu, False jika gagal.

        Contoh:
            >>> audio = DrumAudio()
            >>> audio.play("snare")  # mainkan snare saat mata kiri berkedip
        """
        if sound_type not in self.sounds:
            print(f"⚠️ Warning: Tipe suara '{sound_type}' tidak dikenali. "
                  f"Pilihan valid: {list(self.sounds.keys())}")
            return False
        
        try:
            # Cari channel kosong (hindari overlap suara)
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(self.sounds[sound_type])
                return True
            else:
                # Jika semua channel penuh, mainkan di channel 0 (override)
                pygame.mixer.Channel(0).play(self.sounds[sound_type])
                return True
        except Exception as e:
            print(f"⚠️ Error saat memainkan '{sound_type}': {e}")
            return False

    def is_playing(self) -> bool:
        """
        Memeriksa apakah sedang ada suara yang diputar.

        Returns:
            bool: True jika minimal satu channel sedang memutar suara.
        """
        return pygame.mixer.get_busy()

    def cleanup(self) -> None:
        """
        Membersihkan resource audio.
        Harus dipanggil sebelum program berakhir untuk mencegah memory leak.
        """
        pygame.mixer.quit()
        print("🔇 Audio resource dibersihkan.")