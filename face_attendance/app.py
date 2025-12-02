from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import time
from datetime import datetime
import config
from face_recognition_system import FaceRecognitionSystem

app = Flask(__name__)

# Yuzni tanib olish tizimini ishga tushirish
face_system = FaceRecognitionSystem()

# Video kamera
camera = None
camera_lock = threading.Lock()

# O'zgaruvchilar
frame_counter = 0
last_recognized = {}  # So'nggi tanilgan yuzlar (spam oldini olish uchun)


def get_camera():
    """
    Kamerani ishga tushirish
    """
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, config.VIDEO_FPS)
    return camera


def generate_frames():
    """
    Video streamni generatsiya qilish (real-time)
    """
    global frame_counter, last_recognized

    camera = get_camera()

    while True:
        with camera_lock:
            success, frame = camera.read()

        if not success:
            break

        frame_counter += 1

        # Har N-kadrda yuzni tanib olish (tezlik uchun)
        if frame_counter % config.PROCESS_EVERY_N_FRAMES == 0:
            # Yuzlarni tanib olish
            results = face_system.recognize_faces_in_frame(frame)

            # Har bir yuzni chizish va davomat qilish
            for result in results:
                name = result['name']
                student_id = result['student_id']
                top, right, bottom, left = result['location']
                distance = result['distance']

                # Yuzning atrofiga to'rtburchak chizish
                color = (0, 255, 0) if name != "Noma'lum" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                # Ism va aniqlik ko'rsatish
                confidence = int((1 - distance) * 100)
                label = f"{name} ({confidence}%)"
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, label, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

                # Davomat qilish (agar tanilgan bo'lsa va spam bo'lmasa)
                if student_id and name != "Noma'lum":
                    current_time = time.time()

                    # Spam oldini olish (har 30 soniyada bir marta)
                    if student_id not in last_recognized or \
                            (current_time - last_recognized[student_id]) > 30:
                        face_system.mark_attendance(student_id, name)
                        last_recognized[student_id] = current_time

        # Frame'ni encode qilish
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()

        # Stream uchun yield qilish
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# ===== ROUTE'LAR =====

@app.route('/')
def index():
    """
    Asosiy sahifa
    """
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """
    Video stream
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/status')
def get_status():
    """
    Tizim holati haqida ma'lumot
    """
    status = {
        'encodings_loaded': len(face_system.known_face_encodings) > 0,
        'total_students': len(set(face_system.known_face_ids)),
        'total_encodings': len(face_system.known_face_encodings),
        'camera_active': camera is not None and camera.isOpened(),
        'config': {
            'model': config.FACE_RECOGNITION_MODEL,
            'tolerance': config.FACE_MATCH_TOLERANCE,
            'frame_scale': config.FRAME_SCALE
        }
    }
    return jsonify(status)


@app.route('/api/create_encodings', methods=['POST'])
def create_encodings():
    """
    Encoding'larni qayta yaratish
    """
    try:
        success = face_system.create_encodings_from_dataset()

        if success:
            return jsonify({
                'success': True,
                'message': 'Encoding\'lar muvaffaqiyatli yaratildi',
                'total': len(face_system.known_face_encodings)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Encoding yaratishda xatolik'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/attendance_today')
def get_attendance_today():
    """
    Bugungi davomat ro'yxati
    """
    import csv
    from datetime import date

    today = date.today().strftime(config.ATTENDANCE_DATE_FORMAT)
    attendance_list = []

    try:
        if os.path.exists(config.ATTENDANCE_FILE):
            with open(config.ATTENDANCE_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Date'] == today:
                        attendance_list.append({
                            'student_id': row['Student_ID'],
                            'name': row['Name'],
                            'time': row['Time']
                        })

        return jsonify({
            'success': True,
            'date': today,
            'count': len(attendance_list),
            'attendance': attendance_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/students')
def get_students():
    """
    Barcha talabalar ro'yxati
    """
    students = []
    seen = set()

    for i, student_id in enumerate(face_system.known_face_ids):
        if student_id not in seen:
            students.append({
                'id': student_id,
                'name': face_system.known_face_names[i],
                'encodings_count': face_system.known_face_ids.count(student_id)
            })
            seen.add(student_id)

    return jsonify({
        'success': True,
        'total': len(students),
        'students': students
    })


# ===== DASTURNI ISHGA TUSHIRISH =====

def cleanup():
    """
    Dastur yopilganda kamerani to'xtatish
    """
    global camera
    if camera is not None:
        camera.release()
        print("🎥 Kamera to'xtatildi")


if __name__ == '__main__':
    import atexit
    import os

    atexit.register(cleanup)

    print("\n" + "=" * 60)
    print("🚀 YUZNI TANIB OLISH TIZIMI ISHGA TUSHIRILDI")
    print("=" * 60)
    print(f"🌐 URL: http://localhost:{config.FLASK_PORT}")
    print(f"📊 Talabalar soni: {len(set(face_system.known_face_ids))}")
    print(f"🎯 Encoding'lar: {len(face_system.known_face_encodings)}")
    print("=" * 60)

    # Agar encoding'lar bo'lmasa, ogohlantirish
    if not face_system.known_face_encodings:
        print("\n⚠️  DIQQAT: Encoding'lar topilmadi!")
        print("📝 Dataset papkasiga talabalar rasmlarini joylashtiring")
        print(f"📁 Dataset: {config.DATASET_DIR}")
        print("🔧 Keyin web interfacedan 'Create Encodings' tugmasini bosing")
        print()

    app.run(
        host='0.0.0.0',
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        threaded=True
    )