import numpy as np
import pygame
import time
import speech_recognition as sr
import sounddevice as sd
from pydub import AudioSegment
from audio_manager import AudioManager

audio_manager = AudioManager()

audio_path = "NEW!!!!!/sounds/5.mp3"

def detect_word_from_mic(target_words=["蘇", "書", "酥", "甦", "輸", "舒", "super", "Super"]):
    """
    偵測麥克風輸入中的目標字，並播放音效。
    """
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            print("請開始說話...")
            try:
                audio = recognizer.listen(source, timeout=2)  # 增加 timeout 時間
                print("正在辨識語音...")
                text = recognizer.recognize_google(audio, language="zh-TW")
                print(f"辨識結果: {text}")
                if any(word in text for word in target_words):
                    print(f"偵測到目標字: {text}")
                    audio_manager.play_audio(priority=1, audio_path=audio_path)  # 優先級設為 1
            except sr.UnknownValueError:
                print("無法辨識語音")
            except sr.RequestError as e:
                print(f"語音服務錯誤: {e}")
            except Exception as e:
                print(f"發生錯誤: {e}")

def start_super(target_words):
    """
    啟動語音偵測功能。
    """
    detect_word_from_mic(target_words)
