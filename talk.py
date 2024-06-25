import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import pyaudio
import threading
import time
import pyautogui
import pyperclip
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Suara ke Tulisan")

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.text_area = tk.Text(self.frame, wrap=tk.WORD, width=50, height=2, font=("Times New Roman", 12))
        self.text_area.pack(padx=10, pady=10)

        self.mic_label = tk.Label(self.frame, text="Pilih Microphone:", font=("Times New Roman", 12))
        self.mic_label.pack(pady=5)

        self.mic_combo = ttk.Combobox(self.frame, font=("Times New Roman", 12))
        self.mic_combo.pack(pady=5)
        self.populate_microphones()

        self.listen_button = tk.Button(self.frame, text="Mulai Bicara", command=self.start_listening, font=("Times New Roman", 12))
        self.listen_button.pack(pady=10)

        self.stop_button = tk.Button(self.frame, text="Berhenti Bicara", command=self.stop_listening, font=("Times New Roman", 12))
        self.stop_button.pack(pady=10)

        self.recognizer = sr.Recognizer()
        self.listening = False
        self.speech_detected = False

    def populate_microphones(self):
        p = pyaudio.PyAudio()
        mic_list = []
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                mic_list.append(device_info['name'])
        self.mic_combo['values'] = mic_list
        if mic_list:
            self.mic_combo.current(0)
        logging.debug(f"Microphone yang terdeteksi: {mic_list}")

    def recognize_speech_from_mic(self):
        selected_mic_index = self.mic_combo.current()
        p = pyaudio.PyAudio()
        device_info = p.get_device_info_by_index(selected_mic_index)
        mic = sr.Microphone(device_index=device_info['index'])

        with mic as source:
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, "Silahkan Bicara...\n")
            self.text_area.see(tk.END)
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

        try:
            text = self.recognizer.recognize_google(audio, language="id-ID")  # Set language to Indonesian
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, f"Output: {text}\n")
            pyperclip.copy(text)  # Copy recognized text to clipboard
            logging.debug(f"Kata Yang Terbaca: {text}")
            pyautogui.write(text)  # Write recognized text to Notepad or other text editor
            self.speech_detected = True  # Set flag indicating that speech was detected
            self.last_speech_time = time.time()  # Update last speech time
        except sr.UnknownValueError:
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, "Suaranya Ga Jelas atau Kurang Kenceng\n")
            logging.error("Suaranya Ga Jelas atau Kurang Kenceng")
        except sr.RequestError as e:
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, f"Could not request results from Google Speech Recognition service; {e}\n")
            logging.error(f"Could not request results from Google Speech Recognition service; {e}")

    def check_speech_end(self):
        while self.listening:
            if self.speech_detected and time.time() - self.last_speech_time > 2:  # 2 seconds of silence after speech detected
                pyautogui.press('enter')  # Press enter after 2 seconds of silence
                self.speech_detected = False  # Reset speech detected flag
            time.sleep(0.1)  # Check more frequently for better responsiveness

    def start_listening(self):
        if not self.listening:
            self.listening = True
            self.last_speech_time = time.time()  # Reset last speech time
            threading.Thread(target=self.recognize_speech_thread).start()
            threading.Thread(target=self.check_speech_end).start()

    def stop_listening(self):
        self.listening = False
        logging.debug("Stopped listening")

    def recognize_speech_thread(self):
        while self.listening:
            self.recognize_speech_from_mic()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()
