import cv2

# Inisialisasi webcam (0 = kamera default)
cap = cv2.VideoCapture(0)

print("Tekan tombol 'q' pada keyboard untuk keluar")

while True:
    # Baca frame dari webcam
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Tidak bisa mengakses webcam")
        break
        
    # Tampilkan frame di window
    cv2.imshow('Webcam Test - Tekan q untuk keluar', frame)
    
    # Jika tombol 'q' ditekan, keluar dari loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan resource
cap.release()
cv2.destroyAllWindows()
print("Program selesai. Webcam ditutup.")