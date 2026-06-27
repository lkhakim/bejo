import cv2
import os
import pickle
import threading
import time
import logging

logger = logging.getLogger("bejo.face")

try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False

FACES_DB = "faces_db.pkl"


class FaceDetector:
    def __init__(self, on_face_detected=None, interval=2.0, cooldown=30.0):
        self.on_face_detected = on_face_detected
        self.interval = interval
        self.cooldown = cooldown
        self.running = False
        self.thread = None
        self._last_greet = 0.0
        self._face_cascade = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Face detector started")

    def stop(self):
        self.running = False
        logger.info("Face detector stopped")

    def _load_cascade(self):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            self._face_cascade = cv2.CascadeClassifier(cascade_path)
            return True
        logger.warning("Haar cascade not found at %s", cascade_path)
        return False

    def _run(self):
        if not self._load_cascade():
            return

        cap = None
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                logger.warning("Camera not available for face detection")
                return
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            cap.set(cv2.CAP_PROP_FPS, 5)

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(self.interval)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self._face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
                )

                if len(faces) > 0 and self.on_face_detected:
                    now = time.time()
                    if now - self._last_greet >= self.cooldown:
                        self._last_greet = now
                        self.on_face_detected()

                time.sleep(self.interval)

        except Exception as e:
            logger.error(f"Face detector error: {e}")
        finally:
            if cap:
                cap.release()


def register_face(name: str) -> str:
    if not FACE_REC_AVAILABLE:
        return "Waduh Bos, library 'face-recognition' belum terinstal. Saya belum bisa liat wajah nih."

    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print(f"Bejo: Bos, tolong lihat ke kamera ya. Mau saya foto buat kenalan sama {name}...")

    ret, frame = video_capture.read()
    video_capture.release()

    if not ret:
        return "Gagal mengakses kamera, Bos. Mungkin kameranya lagi dipake aplikasi lain?"

    face_locations = face_recognition.face_locations(frame)
    if not face_locations:
        return "Aduh Bos, wajahnya nggak kelihatan. Coba lebih terang atau hadap depan ya."

    face_encodings = face_recognition.face_encodings(frame, face_locations)

    db = {}
    if os.path.exists(FACES_DB):
        with open(FACES_DB, "rb") as f:
            db = pickle.load(f)

    db[name] = face_encodings[0]

    with open(FACES_DB, "wb") as f:
        pickle.dump(db, f)

    return f"Sip! Bejo sudah hafal wajahnya {name}. Nanti kalau ketemu lagi pasti Bejo sapa."


def identify_person() -> str:
    if not FACE_REC_AVAILABLE:
        return "Waduh Bos, library 'face-recognition' belum terinstal. Saya belum bisa liat wajah nih."

    if not os.path.exists(FACES_DB):
        return "Bejo belum kenal siapa-siapa nih, Bos. Daftarin dulu dong!"

    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("Bejo: Coba sini liat kamera, Bejo tebak siapa...")

    ret, frame = video_capture.read()
    video_capture.release()

    if not ret:
        return "Kameranya ngambek, Bos. Nggak bisa liat apa-apa."

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    if not face_encodings:
        return "Nggak ada orang di depan kamera, Bos. Hantu ya?"

    with open(FACES_DB, "rb") as f:
        db = pickle.load(f)

    known_encodings = list(db.values())
    known_names = list(db.keys())

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]
            return f"Wah! Ini kan {name}! Halo {name}, apa kabar?"

    return "Waduh, Bejo nggak kenal nih siapa. Orang asing ya, Bos? Jangan-jangan maling!"
