"""
face_attendance_sessions.py

- Uses face_recognition + OpenCV (light version: small frame scale for speed)
- Logs arrival and departure times per person (multiple sessions allowed)
- Writes full session table to 'attendance_sessions.csv'

Requirements:
pip install opencv-python face_recognition numpy
"""

import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime, timedelta
import csv

# ---------- Settings ----------
IMAGE_PATH = '../images'  # your folder with reference images
FRAME_SCALE = 0.9            # scale factor for recognition (speed vs accuracy) aniqlikni sohirish uchun
TOLERANCE = 0.5                 # face_recognition tolerance
DEPARTURE_TIMEOUT = 10          # seconds of not-seen -> considered 'left'
OUTPUT_CSV = 'attendance_sessions.csv'
# -------------------------------

# --- Load reference images & names ---
images = []
names = []
for file in os.listdir(IMAGE_PATH):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        img = cv2.imread(os.path.join(IMAGE_PATH, file))
        if img is None:
            continue
        images.append(img)
        names.append(os.path.splitext(file)[0])

print("Loaded:", names)

# --- Encode known faces ---
def encode_faces(imgs):
    encs = []
    for img in imgs:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encs = face_recognition.face_encodings(rgb)
        if face_encs:
            encs.append(face_encs[0])
        else:
            encs.append(None)
    return encs

known_encodings = encode_faces(images)
# Filter out None encodings and keep parallel lists
filtered_encodings = []
filtered_names = []
for enc, nm in zip(known_encodings, names):
    if enc is not None:
        filtered_encodings.append(enc)
        filtered_names.append(nm)
known_encodings = filtered_encodings
names = filtered_names

print("Encodings ready for:", names)

# --- Session data structures ---
# sessions: list of dicts {name, arrival:datetime, departure:datetime or None}
sessions = []

# active: maps name -> {arrival: datetime, last_seen: datetime, session_index: int}
active = {}

# --- CSV save/load helpers ---
def save_sessions_to_csv(path=OUTPUT_CSV):
    """Write all sessions to CSV (overwrites). Columns: name,arrival,departure"""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'arrival', 'departure'])
        for s in sessions:
            arr_str = s['arrival'].strftime('%Y-%m-%d %H:%M:%S')
            dep_str = s['departure'].strftime('%Y-%m-%d %H:%M:%S') if s['departure'] else ''
            writer.writerow([s['name'], arr_str, dep_str])

def load_sessions_from_csv(path=OUTPUT_CSV):
    """Load previous sessions (if exist) to allow persistence across restarts."""
    if not os.path.exists(path):
        return []
    loaded = []
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            arr = datetime.strptime(row['arrival'], '%Y-%m-%d %H:%M:%S')
            dep = datetime.strptime(row['departure'], '%Y-%m-%d %H:%M:%S') if row['departure'] else None
            loaded.append({'name': row['name'], 'arrival': arr, 'departure': dep})
    return loaded

# load previous sessions (optional)
sessions = load_sessions_from_csv()

# --- Mark arrival (create new session) ---
def mark_arrival(name, now):
    # create session record, add to sessions and active
    sess = {'name': name, 'arrival': now, 'departure': None}
    sessions.append(sess)
    active[name] = {'arrival': now, 'last_seen': now, 'session_index': len(sessions)-1}
    print(f"[ARRIVAL] {name} at {now.strftime('%H:%M:%S')}")
    save_sessions_to_csv()

# --- Mark departure (close session) ---
def mark_departure(name, now):
    info = active.get(name)
    if not info:
        return
    idx = info['session_index']
    sessions[idx]['departure'] = now
    # remove from active
    del active[name]
    print(f"[DEPARTURE] {name} at {now.strftime('%H:%M:%S')}")
    save_sessions_to_csv()

# --- Main camera loop ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # small frame for recognition speed
        small = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        # detect faces and encodings on small frame
        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        now = datetime.now()

        seen_this_frame = set()

        for face_encoding, face_loc in zip(face_encodings, face_locations):
            # compare to known
            if not known_encodings:
                continue
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_idx = np.argmin(distances)
            if distances[best_idx] <= TOLERANCE:
                name = names[best_idx]
            else:
                name = "UNKNOWN"

            # map location back to full frame for drawing
            top, right, bottom, left = face_loc
            top = int(top / FRAME_SCALE); right = int(right / FRAME_SCALE)
            bottom = int(bottom / FRAME_SCALE); left = int(left / FRAME_SCALE)

            # draw
            color = (0,255,0) if name != "UNKNOWN" else (0,0,255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name.upper(), (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # process arrival/active logic only for known people (skip UNKNOWN)
            if name != "UNKNOWN":
                seen_this_frame.add(name)
                if name in active:
                    # update last seen
                    active[name]['last_seen'] = now
                else:
                    # new arrival
                    mark_arrival(name, now)

        # Check for departures: anyone active but not seen recently
        to_remove = []
        for name, info in list(active.items()):
            last_seen = info['last_seen']
            if (now - last_seen).total_seconds() > DEPARTURE_TIMEOUT:
                # consider departed
                mark_departure(name, now)

        # Optionally: show a small status panel of active people
        y = 20
        cv2.putText(frame, f"Active: {len(active)}  Sessions: {len(sessions)}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 2)
        y += 25
        for i, (name, info) in enumerate(active.items()):
            if i >= 5: break
            txt = f"{name} (seen {int((now - info['last_seen']).total_seconds())}s ago)"
            cv2.putText(frame, txt, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)
            y += 20

        cv2.imshow("Attendance (arrival/departure)", frame)

        # ESC to break
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    # Ensure active people are closed as departed on shutdown (optional)
    shutdown_time = datetime.now()
    for name in list(active.keys()):
        mark_departure(name, shutdown_time)
    print("Exiting, sessions saved to", OUTPUT_CSV)
