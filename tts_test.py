from gtts import gTTS
import os

text = "എന്റെ പേര് അനന്യ"

tts = gTTS(text=text, lang='ml')
tts.save("sentence.mp3")

print("Audio file generated!")

# Play audio (Windows)
os.system("start sentence.mp3")