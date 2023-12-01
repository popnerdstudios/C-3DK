import speech_recognition as sr
import time

r = sr.Recognizer()

keywords = [("google", 1), ("hey google", 1), ]

source = sr.Microphone()


def callback(recognizer, audio):  # this is called from the background thread

    try:
        speech_as_text = recognizer.recognize_sphinx(audio, keyword_entries=keywords)
        print(speech_as_text)

        # Look for your "Ok Google" keyword in speech_as_text
        if "google" in speech_as_text or "hey google":
            recognize_main()

    except sr.UnknownValueError:
        print("Oops! Didn't catch that")


def recognize_main():
    print("Recognizing Main...")
    audio_data = r.listen(source)
    print(audio_data)

def start_recognizer():
    r.listen_in_background(source, callback)
    time.sleep(1000000)


start_recognizer()