import face_recognition
import pickle
import os

images_path = "images"

known_encodings = []
known_names = []

# Iterate through each image in the folder
for file_name in os.listdir(images_path):
    img_path = os.path.join(images_path, file_name)

    # Skip non-image files
    if not (file_name.lower().endswith(".jpg") or
            file_name.lower().endswith(".jpeg") or
            file_name.lower().endswith(".png")):
        continue

    # Extract name from file (e.g., Abdulaziz.jpg → Abdulaziz)
    person_name = os.path.splitext(file_name)[0]

    try:
        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            encoding = encodings[0]
            known_encodings.append(encoding)
            known_names.append(person_name)
            print(f"[OK] Encoded: {person_name}")
        else:
            print(f"[WARN] No face found in {file_name}")

    except Exception as e:
        print(f"[ERROR] {file_name} ni o‘qishda xato: {e}")

# Save encodings to pkl
data = {"encodings": known_encodings, "names": known_names}

with open("encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print("\nEncoding tugadi! Fayl: encodings.pkl")
