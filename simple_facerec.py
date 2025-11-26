import cv2
import face_recognition

def SimpleFacerec():

    img = cv2.imread("images/Lionel_Messi.jpg")
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb)[0]

    img2 = cv2.imread("images/Lionel_Messi.jpg")
    rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    encodings2 = face_recognition.face_encodings(rgb)[0]

    result = face_recognition.compare_faces([encodings], encodings2)
    print("Results: ", result)

    cv2.imshow("Image", img)
    cv2.imshow("Image2", img2)
    cv2.waitKey(0)