import mediapipe as mp
import cv2
import numpy as np

class BlinkDetector:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [263, 387, 385, 362, 380, 373]

        self.EAR_THRESHOLD = 0.25   # batas blink
        self.CLOSED_FRAMES = 0
        self.CLOSED_NEEDED = 2      # tahan 2 frame untuk dianggap blink

    def __del__(self):
        self.face_mesh.close()

    def get_EAR(self, eye_points):
        # eye_points = [p1, p2, ..., p6]
        v1 = np.linalg.norm(eye_points[1] - eye_points[5])
        v2 = np.linalg.norm(eye_points[2] - eye_points[4])
        h = np.linalg.norm(eye_points[0] - eye_points[3])
        EAR = (v1 + v2) / (2.0 * h)
        return EAR

    def detect_blinks(self, frame):
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)

        left_blink = False
        right_blink = False
        both_blink = False

        left_pos = (0, 0)
        right_pos = (0, 0)

        if result.multi_face_landmarks:
            face = result.multi_face_landmarks[0]

            left_eye = []
            right_eye = []

            for idx in self.LEFT_EYE:
                lm = face.landmark[idx]
                left_eye.append(np.array([lm.x * w, lm.y * h]))

            for idx in self.RIGHT_EYE:
                lm = face.landmark[idx]
                right_eye.append(np.array([lm.x * w, lm.y * h]))

            left_EAR = self.get_EAR(left_eye)
            right_EAR = self.get_EAR(right_eye)

            # Titik tengah mata
            left_pos = (int(left_eye[0][0]), int(left_eye[0][1]))
            right_pos = (int(right_eye[3][0]), int(right_eye[3][1]))

            # Deteksi kedipan
            if left_EAR < self.EAR_THRESHOLD:
                left_blink = True
            if right_EAR < self.EAR_THRESHOLD:
                right_blink = True

            if left_blink and right_blink:
                both_blink = True

            # Tampilkan info
            cv2.putText(frame, f"EAR L: {left_EAR:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"EAR R: {right_EAR:.2f}", (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        return frame, left_blink, right_blink, both_blink, left_pos, right_pos

    def release(self):
        self.face_mesh.close()
