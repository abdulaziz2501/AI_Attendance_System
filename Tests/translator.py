# # translator_async.py
# import asyncio
# from googletrans import Translator
# from ai_modules.stt_module import listen
#
# async def translate_text(text, src='en', dest='uz'):
#     translator = Translator()
#     result = await translator.translate(text, src=src, dest=dest)
#     return result.text
#
# async def main():
#     # samples = [
#     #     "Hello Azizbek, how are you?",
#     #     "This is a simple English to Uzbek translator using googletrans.",
#     #     "Can you help me learn Python and improve my English?"
#     # ]
#
#     text = listen()
#
#     # for s in samples:
#     #     print("EN:", s)
#     #     try:
#     #         uz = await translate_text(s)
#     #         print("UZ:", uz)
#     #     except Exception as e:
#     #         print("Error:", e)
#     #     print("---")
#
#     print("EN:", text)
#     try:
#         uz = await translate_text(text)
#         print("UZ:", uz)
#     except Exception as e:
#         print("Error:", e)
#     print("---")
#
# if __name__ == "__main__":
#     asyncio.run(main())
#


import cv2

# Telefon kamerasi DroidCam orqali: /dev/video0
cap = cv2.VideoCapture(2)

# Face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    cv2.imshow("Camera Face Detection", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
