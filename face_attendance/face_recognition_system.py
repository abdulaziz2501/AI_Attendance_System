import face_recognition
import cv2
import pickle
import os
import numpy as np
from datetime import datetime
from pathlib import Path
import concurrent.futures
import csv
import config


class FaceRecognitionSystem:
    """
    YUZNI TANIB OLISH TIZIMI

    Asosiy vazifalar:
    1. Datasetdan encoding'larni yaratish va saqlash
    2. Real-time yuzni tanib olish
    3. Davomat yozish
    """

    def __init__(self):
        """Tizimni boshlash"""
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []

        # Papkalarni yaratish
        config.create_required_directories()

        # Encoding'larni yuklash (agar mavjud bo'lsa)
        self.load_encodings()

    # ===== 1. ENCODING YARATISH VA SAQLASH =====

    def create_encodings_from_dataset(self):
        """
        Dataset papkasidan barcha rasmlarni o'qib, encoding yaratadi
        va saqlaydi. Bu jarayon FAQAT BIR MARTA bajariladi!

        Dataset strukturasi:
        dataset/
        ├── student_001/
        │   ├── 1.jpg
        │   ├── 2.jpg
        │   └── ...
        ├── student_002/
        └── ...
        """
        print("\n" + "=" * 60)
        print("🔄 ENCODING YARATISH JARAYONI BOSHLANDI...")
        print("=" * 60)

        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []

        # Dataset papkasini tekshirish
        if not os.path.exists(config.DATASET_DIR):
            print("❌ Dataset papkasi topilmadi!")
            return False

        # Har bir talaba papkasini o'qish
        student_folders = [f for f in os.listdir(config.DATASET_DIR)
                           if os.path.isdir(os.path.join(config.DATASET_DIR, f))]

        if not student_folders:
            print("⚠️  Dataset bo'sh!")
            return False

        total_images = 0
        successful_encodings = 0

        # Parallel processing yoki oddiy processing
        if config.USE_PARALLEL_PROCESSING:
            successful_encodings = self._process_dataset_parallel(student_folders)
        else:
            for student_id in student_folders:
                count = self._process_student_folder(student_id)
                successful_encodings += count

        # Natijani saqlash
        if successful_encodings > 0:
            self.save_encodings()
            print("\n" + "=" * 60)
            print(f"✅ MUVAFFAQIYATLI YAKUNLANDI!")
            print(f"📊 Jami talabalar: {len(student_folders)}")
            print(f"📊 Jami encoding'lar: {successful_encodings}")
            print("=" * 60)
            return True
        else:
            print("❌ Encoding yaratilmadi!")
            return False

    def _process_student_folder(self, student_id):
        """
        Bitta talaba papkasidagi barcha rasmlardan encoding yaratadi
        """
        student_path = os.path.join(config.DATASET_DIR, student_id)
        image_files = [f for f in os.listdir(student_path)
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not image_files:
            return 0

        print(f"\n👤 {student_id} - {len(image_files)} ta rasm")

        successful_count = 0

        for image_file in image_files:
            image_path = os.path.join(student_path, image_file)

            try:
                # Rasmni yuklash
                image = face_recognition.load_image_file(image_path)

                # Yuzni topish va encoding yaratish
                face_encodings = face_recognition.face_encodings(
                    image,
                    model=config.FACE_RECOGNITION_MODEL,
                    num_jitters=1  # Tezlik uchun kam qiymat
                )

                if face_encodings:
                    # Birinchi yuzni olish (agar bir nechta yuz bo'lsa)
                    encoding = face_encodings[0]

                    self.known_face_encodings.append(encoding)
                    self.known_face_ids.append(student_id)
                    self.known_face_names.append(f"Talaba_{student_id}")

                    successful_count += 1
                    print(f"  ✅ {image_file} - encoding yaratildi")
                else:
                    print(f"  ⚠️  {image_file} - yuz topilmadi")

            except Exception as e:
                print(f"  ❌ {image_file} - xato: {e}")

        return successful_count

    def _process_dataset_parallel(self, student_folders):
        """
        Parallel processing yordamida tezroq encoding yaratish
        """
        print(f"⚡ Parallel processing ishga tushirildi (CPU cores: {config.NUM_CPU_CORES or 'auto'})")

        with concurrent.futures.ProcessPoolExecutor(
                max_workers=config.NUM_CPU_CORES
        ) as executor:
            results = executor.map(self._process_student_folder, student_folders)

        return sum(results)

    def save_encodings(self):
        """
        Encoding'larni PKL faylga saqlash
        Bu jarayon keyingi ishlatishlar uchun encoding'larni saqlaydi
        """
        data = {
            'encodings': self.known_face_encodings,
            'ids': self.known_face_ids,
            'names': self.known_face_names,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        with open(config.ENCODINGS_FILE, 'wb') as f:
            pickle.dump(data, f)

        print(f"\n💾 Encoding'lar saqlandi: {config.ENCODINGS_FILE}")

    def load_encodings(self):
        """
        Avval saqlangan encoding'larni yuklash
        Agar fayl bo'lmasa, bo'sh ro'yxat qaytaradi
        """
        if os.path.exists(config.ENCODINGS_FILE):
            try:
                with open(config.ENCODINGS_FILE, 'rb') as f:
                    data = pickle.load(f)

                self.known_face_encodings = data['encodings']
                self.known_face_ids = data['ids']
                self.known_face_names = data['names']

                print(f"✅ Encoding'lar yuklandi: {len(self.known_face_encodings)} ta")
                print(f"📅 Yaratilgan: {data.get('created_at', 'Noma\'lum')}")
                return True
            except Exception as e:
                print(f"⚠️  Encoding yuklashda xato: {e}")
                return False
        else:
            print("ℹ️  Encoding fayli topilmadi. Yangi yarating!")
            return False

    # ===== 2. REAL-TIME YUZNI TANIB OLISH =====

    def recognize_faces_in_frame(self, frame):
        """
        Bir kadrda (frame) yuzlarni tanib olish

        Args:
            frame: OpenCV frame (numpy array)

        Returns:
            list: [(name, location), ...] formatida natija
        """
        # Encoding'lar mavjudligini tekshirish
        if not self.known_face_encodings:
            return []

        # Rasmni kichraytirish (tezlik uchun)
        small_frame = cv2.resize(frame, (0, 0), fx=config.FRAME_SCALE, fy=config.FRAME_SCALE)

        # BGR dan RGB ga o'tkazish (face_recognition RGB bilan ishlaydi)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Yuzlarni topish
        face_locations = face_recognition.face_locations(
            rgb_frame,
            number_of_times_to_upsample=config.FACE_DETECTION_UPSAMPLE
        )

        # Yuz encoding'larini yaratish
        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations,
            model=config.FACE_RECOGNITION_MODEL
        )

        # Har bir yuzni taqqoslash
        results = []
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Barcha ma'lum yuzlar bilan taqqoslash
            matches = face_recognition.compare_faces(
                self.known_face_encodings,
                face_encoding,
                tolerance=config.FACE_MATCH_TOLERANCE
            )

            name = "Noma'lum"
            student_id = None

            # Eng yaqin o'xshashlikni topish
            face_distances = face_recognition.face_distance(
                self.known_face_encodings,
                face_encoding
            )

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    student_id = self.known_face_ids[best_match_index]

            # Location'ni asl o'lchamga qaytarish
            top, right, bottom, left = face_location
            top = int(top / config.FRAME_SCALE)
            right = int(right / config.FRAME_SCALE)
            bottom = int(bottom / config.FRAME_SCALE)
            left = int(left / config.FRAME_SCALE)

            results.append({
                'name': name,
                'student_id': student_id,
                'location': (top, right, bottom, left),
                'distance': float(face_distances[best_match_index]) if len(face_distances) > 0 else 1.0
            })

        return results

    # ===== 3. DAVOMAT YOZISH =====

    def mark_attendance(self, student_id, student_name):
        """
        Talabani davomat daftariga yozish

        Args:
            student_id: Talaba ID
            student_name: Talaba ismi
        """
        now = datetime.now()
        date_str = now.strftime(config.ATTENDANCE_DATE_FORMAT)
        time_str = now.strftime(config.ATTENDANCE_TIME_FORMAT)

        # CSV faylni yaratish (agar mavjud bo'lmasa)
        file_exists = os.path.exists(config.ATTENDANCE_FILE)

        # Bugungi davomat mavjudligini tekshirish
        if file_exists and config.UNIQUE_ATTENDANCE_PER_DAY:
            with open(config.ATTENDANCE_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3 and row[0] == student_id and row[2] == date_str:
                        print(f"ℹ️  {student_name} bugun allaqachon qayd qilingan")
                        return False

        # Davomat yozish
        with open(config.ATTENDANCE_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header yozish (agar yangi fayl bo'lsa)
            if not file_exists:
                writer.writerow(['Student_ID', 'Name', 'Date', 'Time'])

            writer.writerow([student_id, student_name, date_str, time_str])

        print(f"✅ Davomat qayd qilindi: {student_name} ({date_str} {time_str})")
        return True


# ===== ASOSIY SINOV =====
if __name__ == "__main__":
    print("=" * 60)
    print("YUZNI TANIB OLISH TIZIMI - SINOV")
    print("=" * 60)

    # Tizimni yaratish
    system = FaceRecognitionSystem()

    # Encoding'lar mavjud bo'lmasa, yaratish
    if not system.known_face_encodings:
        print("\n⚠️  Encoding'lar topilmadi!")
        print("📝 Dataset papkasiga talabalar rasmlarini joylashtiring")
        print(f"📁 Dataset papkasi: {config.DATASET_DIR}")

        response = input("\n❓ Encoding yaratishni xohlaysizmi? (y/n): ")
        if response.lower() == 'y':
            system.create_encodings_from_dataset()
    else:
        print(f"\n✅ Tizim tayyor! {len(system.known_face_encodings)} ta yuz taniydi")
        print(f"👥 Talabalar: {set(system.known_face_ids)}")