from ai_modules import stt_module, nlp_handler, tts_module

def main():
    print("📢 AI Davomat tizimi tayyor.")
    while True:
        query = stt_module.listen()
        if "chiq" in query:
            tts_module.speak("Yaxshi, tizim yopilmoqda.")
            break
        answer = nlp_handler.handle_query(query)
        print("🤖", answer)
        tts_module.speak(answer)

if __name__ == "__main__":
    main()
