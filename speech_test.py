import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak something...")
    audio = r.listen(source)

try:
    text = r.recognize_google(audio, language="ml-IN")
    print("You said:", text)
except:
    print("Could not understand")