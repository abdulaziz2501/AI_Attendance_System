import os

# ===== PAPKA YO'LLARI =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
ENCODINGS_DIR = os.path.join(BASE_DIR, 'encodings')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Encoding faylining yo'li
ENCODINGS_FILE = os.path.join(ENCODINGS_DIR, 'face_encodings.pkl')

# Davomat CSV fayli
ATTENDANCE_FILE = os.path.join(DATA_DIR, 'attendance.csv')

# ===== YUZNI TANIB OLISH SOZLAMALARI =====

# Model aniqligi (smaller = tezroq, larger = aniqroq)
# 'small' yoki 'large' bo'lishi mumkin
FACE_RECOGNITION_MODEL = 'large'  # OPTIMAL TANLANGAN!

# Yuzni topish aniqligi (0-2 oralig'ida)
# Past qiymat = tezroq lekin kamroq yuz topadi
# Yuqori qiymat = sekinroq lekin ko'proq yuz topadi
FACE_DETECTION_UPSAMPLE = 1  # Default: 1 (optimal)

# O'xshashlik chegarasi (0-1 oralig'ida)
# Past qiymat = qattiqroq (kamroq noto'g'ri tanish)
# Yuqori qiymat = yumshoqroq (ko'proq noto'g'ri tanish)
FACE_MATCH_TOLERANCE = 0.6  # Default: 0.6 (optimal)

# ===== RASM SOZLAMALARI =====

# Rasmlarni kichraytirish (tezlikni oshirish uchun)
# 1.0 = asl o'lcham, 0.5 = 2 marta kichik, 0.25 = 4 marta kichik
FRAME_SCALE = 0.5  # Kamera rasmlarini 2 marta kichraytiramiz

# Har necha kadr oralig'ida yuzni tekshirish
# Yuqori qiymat = tezroq lekin kamroq aniq
PROCESS_EVERY_N_FRAMES = 2  # Har 2-kadrda bir tekshirish

# ===== MULTI-PROCESSING SOZLAMALARI =====

# Parallel processing ishlatish (tezlashtirish uchun)
USE_PARALLEL_PROCESSING = True

# CPU core'lar soni (None = barcha core'lar)
# Agar kompyuter sekin bo'lsa, kamroq qiymat qo'ying
NUM_CPU_CORES = None  # Avtomatik aniqlash

# ===== DAVOMAT SOZLAMALARI =====

# Bir talaba bir kun ichida necha marta qayd qilinishi
# True = faqat birinchi kirish, False = har safar
UNIQUE_ATTENDANCE_PER_DAY = True

# Davomat saqlanish formati
ATTENDANCE_DATE_FORMAT = '%Y-%m-%d'
ATTENDANCE_TIME_FORMAT = '%H:%M:%S'

# ===== WEB INTERFACE SOZLAMALARI =====

# Flask server porti
FLASK_PORT = 5000
FLASK_DEBUG = True

# Video stream FPS
VIDEO_FPS = 30

# ===== XAVFSIZLIK =====

# Maksimal rasm hajmi (MB)
MAX_IMAGE_SIZE_MB = 5

# Qabul qilinadigan rasm formatlari
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# ===== LOGGING =====

# Log darajasi: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# Log fayl yo'li
LOG_FILE = os.path.join(BASE_DIR, 'attendance_system.log')


# ===== KERAKLI PAPKALARNI YARATISH =====
def create_required_directories():
    """
    Tizim ishlashi uchun kerakli papkalarni yaratadi
    """
    directories = [DATASET_DIR, ENCODINGS_DIR, DATA_DIR]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Papka yaratildi: {directory}")
        else:
            print(f"📁 Papka mavjud: {directory}")


if __name__ == "__main__":
    # Test uchun
    create_required_directories()
    print("\n" + "=" * 50)
    print("TIZIM SOZLAMALARI:")
    print("=" * 50)
    print(f"📊 Model: {FACE_RECOGNITION_MODEL}")
    print(f"🎯 O'xshashlik chegarasi: {FACE_MATCH_TOLERANCE}")
    print(f"🖼️  Rasm masshtabi: {FRAME_SCALE}")
    print(f"⚡ Parallel processing: {USE_PARALLEL_PROCESSING}")
    print(f"🔄 Har {PROCESS_EVERY_N_FRAMES} kadrda tekshirish")
    print("=" * 50)