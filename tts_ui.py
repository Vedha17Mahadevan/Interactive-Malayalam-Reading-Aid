import tkinter as tk
from tkinter import ttk
import pygame
from gtts import gTTS
import speech_recognition as sr
import os

pygame.mixer.init()

# -------- ROOT --------
root = tk.Tk()
root.title("Malayalam Reading Assistant")
root.geometry("1100x720")
root.configure(bg="#eef5f9")

# -------- SETUP --------
os.makedirs("audio/words", exist_ok=True)
os.makedirs("audio/sentences", exist_ok=True)

words = []
sentence_text = ""
click_count = {}

preset_texts = {
    "Easy": "എന്റെ പേര് അനന്യ ആണ്",
    "Medium": "എനിക്ക് മലയാളം വായിക്കാൻ ഇഷ്ടമാണ്",
    "Hard": "കുട്ടികൾ പുസ്തകം വായിക്കുന്നത് അവരുടെ ഭാഷാ കഴിവുകൾ മെച്ചപ്പെടുത്താൻ സഹായിക്കുന്നു"
}

# -------- AUDIO --------
def get_word_audio(word):
    path = f"audio/words/{word}.mp3"
    if not os.path.exists(path):
        gTTS(text=word, lang='ml').save(path)
    return path

def get_sentence_audio(sentence):
    path = "audio/sentences/sentence.mp3"
    if not os.path.exists(path):
        gTTS(text=sentence, lang='ml').save(path)
    return path

# -------- PLAY WORD --------
def play_word(index):
    word = words[index]
    click_count[word] = click_count.get(word, 0) + 1

    for i in range(len(words)):
        text_widget.tag_config(f"word_{i}", background="white")

    text_widget.tag_config(f"word_{index}", background="#ffe066")

    pygame.mixer.music.load(get_word_audio(word))
    pygame.mixer.music.play()

    update_stats()

# -------- PLAY SENTENCE --------
def play_sentence():
    pygame.mixer.music.load(get_sentence_audio(sentence_text))
    pygame.mixer.music.play()

# -------- LOAD TEXT --------
def load_text():
    global words, sentence_text, click_count

    click_count = {}

    if mode.get() == "preset":
        sentence_text = preset_texts[selected_preset.get()]
    else:
        sentence_text = input_box.get("1.0", tk.END).strip()

    words = sentence_text.split()

    text_widget.config(state="normal")
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", sentence_text)

    start_index = "1.0"
    for i, word in enumerate(words):
        pos = text_widget.search(word, start_index, stopindex=tk.END)
        if pos:
            end = f"{pos}+{len(word)}c"
            tag = f"word_{i}"

            text_widget.tag_add(tag, pos, end)
            text_widget.tag_bind(tag, "<Button-1>", lambda e, i=i: play_word(i))
            text_widget.tag_config(tag, foreground="blue", underline=True)

            start_index = end

    text_widget.config(state="disabled")

    update_stats()
    result_label.config(text="")

# -------- LIVE STATS --------
def update_stats():
    stats_box.config(state="normal")
    stats_box.delete("1.0", tk.END)

    stats_box.insert(tk.END, "📊 Word Click Tracking\n\n")

    for w in words:
        stats_box.insert(tk.END, f"{w} → {click_count.get(w,0)} clicks\n")

    stats_box.config(state="disabled")

# -------- FINAL ANALYSIS --------
def show_result():
    if not click_count:
        result_label.config(text="No data yet.")
        return

    most_diff = max(click_count, key=click_count.get)
    clicks = click_count[most_diff]
    total_clicks = sum(click_count.values())

    if total_clicks < len(words):
        level = "🟢 Easy"
    elif total_clicks < len(words) * 2:
        level = "🟡 Moderate"
    else:
        level = "🔴 Difficult"

    result_label.config(
        text=f"Most Difficult: {most_diff}\nClicks: {clicks}\nLevel: {level}"
    )

# -------- SPEECH RECORD --------
def record_speech():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            result_label.config(text="🎤 Listening... Speak clearly")
            root.update()

            r.adjust_for_ambient_noise(source, duration=1)  # 🔥 important
            audio = r.listen(source, timeout=5, phrase_time_limit=6)

        spoken_text = r.recognize_google(audio, language="ml-IN")

        print("DEBUG:", spoken_text)

        result_label.config(text=f"You said:\n{spoken_text}")

        compare_text(spoken_text)

    except sr.WaitTimeoutError:
        result_label.config(text="⏱️ No speech detected")

    except sr.UnknownValueError:
        result_label.config(text="❌ Could not understand Malayalam")

    except sr.RequestError:
        result_label.config(text="🌐 Network error")

    except Exception as e:
        print("ERROR:", e)
        result_label.config(text="⚠️ Try speaking again")

# -------- COMPARE --------
def normalize_malayalam(word):
    # normalize common variations
    word = word.replace("ൻറെ", "ന്റെ")
    word = word.replace("ന്‍റെ", "ന്റെ")
    word = word.replace("ണ്‍", "ൺ")
    return word
def is_similar(w1, w2):
    w1 = normalize_malayalam(w1)
    w2 = normalize_malayalam(w2)

    return w1 == w2 or w1 in w2 or w2 in w1

def compare_text(spoken_text):
    spoken_words = spoken_text.split()

    text_widget.config(state="normal")

    # reset colors
    for i in range(len(words)):
        text_widget.tag_config(f"word_{i}", foreground="blue")

    for i in range(len(words)):
        if i >= len(spoken_words):
            text_widget.tag_config(f"word_{i}", foreground="red")
        elif not is_similar(words[i], spoken_words[i]):
            text_widget.tag_config(f"word_{i}", foreground="red")

    text_widget.config(state="disabled")
# -------- TOP UI --------
tk.Label(root, text="Malayalam Reading Assistant",
         font=("Arial", 18, "bold"),
         bg="#eef5f9").pack(pady=10)

mode = tk.StringVar(value="preset")

top_frame = tk.Frame(root, bg="#eef5f9")
top_frame.pack()

tk.Radiobutton(top_frame, text="Preset", variable=mode, value="preset", bg="#eef5f9").pack(side="left")
tk.Radiobutton(top_frame, text="Custom", variable=mode, value="custom", bg="#eef5f9").pack(side="left")

selected_preset = tk.StringVar(value="Easy")

ttk.Combobox(root, textvariable=selected_preset,
             values=list(preset_texts.keys()),
             state="readonly").pack(pady=5)

input_box = tk.Text(root, height=3)
input_box.pack(padx=20, pady=5)

tk.Button(root, text="Load Text", command=load_text,
          bg="#1976d2", fg="white").pack(pady=5)

# 🎤 MIC BUTTON
tk.Button(root, text="🎤 Start Recording",
          command=record_speech,
          bg="#6a1b9a", fg="white").pack(pady=5)

# -------- MAIN --------
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=1)

# LEFT
left_frame = tk.Frame(main_frame, bg="white", bd=2, relief="solid")
left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

text_widget = tk.Text(left_frame, font=("Arial", 20))
text_widget.pack(fill="both", expand=True, padx=10, pady=10)
text_widget.config(state="disabled")

tk.Button(left_frame, text="🔊 Play Sentence",
          command=play_sentence).pack(pady=5)

# RIGHT
right_frame = tk.Frame(main_frame, bg="#ffd6e0", bd=2, relief="solid")
right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

top_right = tk.Frame(right_frame, bg="#ffd6e0")
top_right.pack(fill="both", expand=True)

bottom_right = tk.Frame(right_frame, bg="#ffd6e0")
bottom_right.pack(fill="x")

stats_box = tk.Text(top_right, font=("Arial", 12), height=10)
stats_box.pack(fill="both", expand=True, padx=10, pady=5)
stats_box.config(state="disabled")

# RESULT CARD
result_frame = tk.Frame(bottom_right, bg="white", bd=1, relief="solid")
result_frame.pack(padx=10, pady=10, fill="x")

tk.Button(result_frame,
          text="Done / Analyze",
          command=show_result,
          bg="#2e7d32",
          fg="white").pack(pady=10)

result_label = tk.Label(result_frame,
                        text="",
                        bg="white",
                        justify="left",
                        wraplength=250)

result_label.pack(padx=10, pady=10)

root.mainloop()