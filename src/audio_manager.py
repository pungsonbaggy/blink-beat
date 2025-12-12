# src/audio_manager.py
import pygame
import os

class DrumAudio:
    def __init__(self):
        pygame.mixer.init()

        # Folder assets/sounds selalu akurat dari lokasi file ini
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sounds_dir = os.path.join(base_dir, "assets", "sounds")  # Pastikan WAV ada di sini

        def make_path(name):
            return os.path.join(sounds_dir, name)

        self.sounds = {}
        files = {
            "kick": "kick.wav",
            "snare": "snare.wav",
            "cymbal": "cymbal.wav",
        }

        for key, fname in files.items():
            path = make_path(fname)
            if os.path.isfile(path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(path)
                    print(f"✅ Suara '{key}' dimuat dari: {path}")
                except Exception as e:
                    self.sounds[key] = None
                    print(f"⚠ Gagal memuat '{path}': {e}")
            else:
                self.sounds[key] = None
                print(f"❌ File tidak ditemukan: {path}")

    def play(self, key):
        snd = self.sounds.get(key)
        if snd:
            snd.play()
        else:
            print(f"⚠ Tidak ada suara untuk key: {key}")

    def cleanup(self):
        try:
            pygame.mixer.quit()
        except:
            pass
