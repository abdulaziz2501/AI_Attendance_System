import cv2
import face_recognition
import sqlite3
from datetime import datetime

def mark_attendance(name):
    conn = sqlite3.connect("data/attendance.db")
    c = conn.cursor()
    now = datetime.now()
    c.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
              (name, now.date(), now.strftime("%H:%M:%S")))
    conn.commit()
    conn.close()

def start_recognition():
    video = cv2.VideoCapture(0)
    known_image = face_recognition.load_image_file("data/students/abdulaziz.jpg")
    known_encoding = face_recognition.face_encodings(known_image)[0]

    while True:
        ret, frame = video.read()
        rgb = frame[:, :, ::-1]
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        for encoding in encodings:
            match = face_recognition.compare_faces([known_encoding], encoding)
            if True in match:
                mark_attendance("Abdulaziz")
                print("✅ Abdulaziz keldi")
        cv2.imshow("Attendance Camera", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
