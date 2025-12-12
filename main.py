import cv2
import pygame
from src.blink_detector import BlinkDetector
from src.audio_manager import DrumAudio
from src.particle_system import ParticleSystem

# ============================================================
# Inisialisasi pygame + mixer (HANYA DI SINI — tidak di audio_manager)
# ============================================================
pygame.init()

# Init mixer aman untuk Windows
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Blink Beat Lite")

# ============================================================
# Inisiasi objek utama
# ============================================================
blink = BlinkDetector()
audio = DrumAudio()     # Tidak memanggil mixer.init lagi
particles = ParticleSystem()
clock = pygame.time.Clock()

# Kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Kamera mirror
    frame = cv2.flip(frame, 1)

    # Deteksi kedipan + posisi mata
    frame, left_blink, right_blink, both_blink, left_pos, right_pos = blink.detect_blinks(frame)

    print("Blink:", left_blink, right_blink, both_blink)


    # Event close pygame window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            quit()

    # LOGIKA SUARA DRUM
    # Kick: kedua mata tertutup
    if both_blink:
        audio.play("kick")
        particles.spawn(400, 300)

    # Snare: mata kiri
    elif left_blink:
        audio.play("snare")
        particles.spawn(300, 300)

    # Cymbal: mata kanan
    elif right_blink:
        audio.play("cymbal")
        particles.spawn(500, 300)

    # ============================================================
    # Kotak mata
    # ============================================================
    if left_pos != (0, 0):
        cv2.rectangle(frame,
                      (left_pos[0] - 10, left_pos[1] - 10),
                      (left_pos[0] + 10, left_pos[1] + 10),
                      (0, 255, 0), 2)

    if right_pos != (0, 0):
        cv2.rectangle(frame,
                      (right_pos[0] - 10, right_pos[1] - 10),
                      (right_pos[0] + 10, right_pos[1] + 10),
                      (0, 255, 0), 2)

    # ============================================================
    # Render Pygame
    # ============================================================
    screen.fill((20, 20, 20))
    particles.draw(screen)
    pygame.display.update()

    # Tampilkan kamera
    cv2.imshow("Camera", frame)

    # Tekan Q untuk keluar kamera
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    clock.tick(60)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
