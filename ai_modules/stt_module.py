import speech_recognition as sr

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Gapiring...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language='uz-UZ')
        print("Siz dedingiz:", text)
        return text.lower()
    except:
        return ""
