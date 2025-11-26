import pyttsx3
from ai_modules.stt_module import listen
#
# # Ovoz mexanizmini ishga tushirish
# engine = pyttsx3.init()
#
# # Ovoz tezligini sozlash
# engine.setProperty('rate', 170)  # 100-200 oralig‘ida bo‘lishi mumkin
#
# # Ovoz tonini (pitch) sozlash
# engine.setProperty('volume', 0.8)  # 0.0 - 1.0 oralig‘ida
#
# # Matnni foydalanuvchidan olish
# text = "mening ismim abdulaziz va men yigirma besh yoshdaman"
#
# # Matnni o‘qib berish
# engine.say(text)
# engine.runAndWait()

#
#
# from ai_modules.stt_module import listen
# # print(listen())
#
# from gtts import gTTS
# import os
#
# text = listen()
# tts = gTTS(text=text)
# print('Audio kiritildi.')
# tts.save("output.mp3")
# os.system("xdg-open output.mp3")  # Windows
# # Linux uchun: os.system("xdg-open output.mp3")
