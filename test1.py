# from ai_modules.stt_module import listen
# print(listen())

#
# from ai_modules.tts_module import speak
# speak("Bugun 24 o‘quvchi keldi.")
# import cv2
#
# video_cap=cv2.VideoCapture(0)
# while True:
#     ret, frame = video_cap.read()
#     cv2.imshow("Video", frame)
#     if cv2.waitKey(1) == ord('q'):
#         break
# video_cap.release()

# import cv2
# import face_recognition
#
# img = cv2.imread("images/Lionel_Messi.jpg")
# rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# encodings = face_recognition.face_encodings(rgb)[0]
#
# img2 = cv2.imread("images/Lionel_Messi.jpg")
# rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
# encodings2 = face_recognition.face_encodings(rgb)[0]
#
# result = face_recognition.compare_faces([encodings], encodings2)
# print("Results: ", result)
#
# cv2.imshow("Image", img)
# cv2.imshow("Image2", img2)
# cv2.waitKey(0)

# import cv2
# from face_recognition import face_locations
#
# from simple_facerec import SimpleFacerec
#
# sfrec = SimpleFacerec()
# sfrec.load_encoding_images("images/")
#
# video_cap=cv2.VideoCapture(0)
# while True:
#     ret, frame = video_cap.read()
#
#     face_locations, face_names = sfrec.detect_known_faces(frame)
#
#     for face_loc, name in zip(face_locations, face_names):
#         y1, x2, y2, x1 = face_loc
#         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
#         cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
#
#     cv2.imshow("Frame", frame)
#     if cv2.waitKey(1) == ord('q'):
#         break
# video_cap.release()

import face_recognition
import cv2
import numpy as np

# This is a super simple (but slow) example of running face recognition on live video from your webcam.
# There's a second example that's a little more complicated but runs faster.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("images/Lionel_Messi.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file("images/Barack_Obama.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding
]
known_face_names = [
    "Lionel messi",
    "Barack Obama"
]

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces and face enqcodings in the frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Loop through each face in this frame of video
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()