import pyaudio
import numpy as np
import pygame
import time
import speech_recognition as sr

def detect_word_from_mic(target_words=["蘇", "書", "酥", "甦", "輸", "舒", "super", "Super"]):
    while True:
        recognized = False
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("請開始說話...")
            try:
                audio = recognizer.listen(source, timeout=0.5)
                print("正在辨識語音...")
                text = recognizer.recognize_google(audio, language="zh-TW")
                print(f"辨識結果: {text}")
                detected_words = [word for word in target_words if word in text]
                if detected_words:
                    print(f"偵測到目標字: {', '.join(detected_words)}")
                    recognized = True
                else:
                    print(f"未偵測到目標字: {', '.join(target_words)}")
            except sr.UnknownValueError:
                print("無法辨識語音")
            except sr.RequestError as e:
                print(f"語音服務錯誤: {e}")
            except Exception as e:
                print(f"發生錯誤: {e}")
        if recognized:
            pygame.mixer.init()
            pygame.mixer.music.load("sounds/super.mp3")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(1)

def start_super():
    detect_word_from_mic(["蘇", "書", "酥", "甦", "輸", "舒", "super", "Super"])
