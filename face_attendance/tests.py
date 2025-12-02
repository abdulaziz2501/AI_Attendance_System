import cv2
import face_recognition
import pickle
import numpy as np
import csv
import os
from datetime import datetime

FRAME_SCALE = 0.5
TOLERANCE = 0.5
DEPARTURE_TIMEOUT = 10
OUTPUT_CSV = 'data/attendance_sessions.csv'
PICKLE_FILE = "encodings/face_encodings.pkl"

# --- Load encodings from pickle ---
print("[INFO] Loading encodings...")
with open(PICKLE_FILE, "rb") as f:
    data = pickle.load(f)
known_encodings = data["encodings"]
known_names = data["names"]
print("[READY] Loaded:", known_names)

# --- Load previous sessions ---
def load_sessions():
    if not os.path.exists(OUTPUT_CSV):
        return []
    sessions = []
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            arr = datetime.strptime(row["arrival"], "%Y-%m-%d %H:%M:%S")
            dep = datetime.strptime(row["departure"], "%Y-%m-%d %H:%M:%S") if row["departure"] else None
            sessions.append({"name": row["name"], "arrival": arr, "departure": dep})
    return sessions

# --- Save ---
def save_sessions(sessions):
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "arrival", "departure"])
        for s in sessions:
            arr = s["arrival"].strftime("%Y-%m-%d %H:%M:%S")
            dep = s["departure"].strftime("%Y-%m-%d %H:%M:%S") if s["departure"] else ""
            writer.writerow([s["name"], arr, dep])

sessions = load_sessions()
active = {}

def mark_arrival(name, now):
    sessions.append({"name": name, "arrival": now, "departure": None})
    active[name] = {"arrival": now, "last_seen": now, "index": len(sessions)-1}
    save_sessions(sessions)
    print(f"[ARRIVAL] {name} at {now.strftime('%H:%M:%S')}")

def mark_departure(name, now):
    idx = active[name]["index"]
    sessions[idx]["departure"] = now
    del active[name]
    save_sessions(sessions)
    print(f"[DEPARTURE] {name} at {now.strftime('%H:%M:%S')}")

# --- Camera ---
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small = cv2.resize(frame, (0, 2), fx=FRAME_SCALE, fy=FRAME_SCALE)
        rgb = small[:, :, ::-1]

        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        now = datetime.now()
        seen = set()

        for enc, loc in zip(encodings, locations):
            distances = face_recognition.face_distance(known_encodings, enc)
            idx = np.argmin(distances)

            name = known_names[idx] if distances[idx] <= TOLERANCE else "UNKNOWN"

            # scale back for drawing
            top, right, bottom, left = loc
            top = int(top / FRAME_SCALE)
            right = int(right / FRAME_SCALE)
            bottom = int(bottom / FRAME_SCALE)
            left = int(left / FRAME_SCALE)

            color = (0,255,0) if name != "UNKNOWN" else (0,0,255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if name != "UNKNOWN":
                seen.add(name)
                if name in active:
                    active[name]["last_seen"] = now
                else:
                    mark_arrival(name, now)

        # departure check
        for person in list(active.keys()):
            last = active[person]["last_seen"]
            if (now - last).total_seconds() > DEPARTURE_TIMEOUT:
                mark_departure(person, now)

        cv2.imshow("Attendance", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    # Close all remaining active sessions
    end = datetime.now()
    for person in list(active.keys()):
        mark_departure(person, end)

    print("[EXIT] All data saved.")
