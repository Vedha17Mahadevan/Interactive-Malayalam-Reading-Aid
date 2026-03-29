from gtts import gTTS
import os

sentence = "എന്റെ പേര് അനന്യ"

words = sentence.split()

# Ensure folders exist
os.makedirs("audio/words", exist_ok=True)
os.makedirs("audio/sentences", exist_ok=True)

# Save sentence audio
tts = gTTS(text=sentence, lang='ml')
tts.save("audio/sentences/sentence.mp3")

# Save word audio
for i, word in enumerate(words):
    tts = gTTS(text=word, lang='ml')
    filename = f"audio/words/word_{i}.mp3"
    tts.save(filename)
    print(f"Saved: {filename}")