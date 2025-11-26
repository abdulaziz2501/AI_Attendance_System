import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime

# --- Rasmlar joylashgan papka ---
path = 'images'
images = []
classNames = []

# --- Rasmlarni yuklash ---
for filename in os.listdir(path):
    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
        img = cv2.imread(f'{path}/{filename}')
        images.append(img)
        classNames.append(os.path.splitext(filename)[0])

print(f"Tanilgan shaxslar: {classNames}")

# --- Yuzlarni kodlash ---
def findEncodings(imgs):
    encodes = []
    for img in imgs:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_encodings(img)
        if faces:
            encodes.append(faces[0])
    return encodes

encodeListKnown = findEncodings(images)
print("Yuz kodlari tayyor ✅")

# --- Davomatni yozish funksiyasi ---
def markAttendance(name):
    with open('attendance.csv', 'a+') as f:
        f.seek(0)
        lines = f.readlines()
        names = [line.split(',')[0] for line in lines]
        if name not in names:
            now = datetime.now()
            timeStr = now.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{name},{timeStr}\n')

# --- Kamera ishga tushirish ---
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 🔹 Kichikroq o‘lcham — tezroq ishlaydi
    smallFrame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    rgbSmallFrame = cv2.cvtColor(smallFrame, cv2.COLOR_BGR2RGB)

    # 🔹 Yuzlarni aniqlash
    facesCur = face_recognition.face_locations(rgbSmallFrame)
    encodesCur = face_recognition.face_encodings(rgbSmallFrame, facesCur)

    for encodeFace, faceLoc in zip(encodesCur, facesCur):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            # Oynaga chizish
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.rectangle(frame, (x1, y2 - 30), (x2, y2), (0, 150, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)

            markAttendance(name)

    cv2.imshow('Face Recognition (Light Version)', frame)

    # ESC bosilsa chiqadi
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
