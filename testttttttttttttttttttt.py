import pyaudio
import numpy as np
import pygame
import time
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QSlider, QComboBox)
from PyQt6.QtCore import Qt, QTimer
import random
import threading

# 從其他檔案匯入所有功能
import super_idol
import meow  
import bad_mic 
import random_song

class AudioSystem:
    def __init__(self):
        self.app = None
        if not QApplication.instance():
            self.app = QApplication([])
        self.threads = {}
        self.running = {}
        
    def start_function(self, name, func):
        if name not in self.running or not self.running[name]:
            if name == "bad_mic":
                # 特殊處理 bad_mic，確保在主執行緒運行
                func()
            else:
                thread = threading.Thread(target=func, daemon=True)
                self.threads[name] = thread
                self.running[name] = True
                thread.start()
            print(f"{name} 已啟動")
        else:
            print(f"{name} 已在運行中")
    
    def stop_function(self, name):
        if name in self.running and self.running[name]:
            self.running[name] = False
            print(f"{name} 已停止")
        else:
            print(f"{name} 未在運行中")

def show_menu():
    audio_system = AudioSystem()

    while True:
        print("\n=== 音訊處理系統選單 ===")
        print("1. 開始 Super idol 偵測器")
        print("2. 開始喵喵回應器")
        print("3. 開始麥克風干擾器")
        print("4. 開始虛擬音9訊輸出")
        print("5. 停止 Super idol 偵測器")
        print("6. 停止喵喵回應器")
        print("7. 停止麥克風干擾器")
        print("8. 停止虛擬音訊輸出")
        print("9. 啟動全部功能")
        print("10. 停止全部功能")
        print("0. 離開")
        
        choice = input("請選擇功能 (0-10): ")
        
        try:
            if choice == "9":
                print("正在啟動所有功能...")
                audio_system.start_function("super_idol", super_idol.start_super())
                audio_system.start_function("meow", meow.meow_start())
                audio_system.start_function("bad_mic", bad_mic.bad_mic_start())
                audio_system.start_function("virtual_out", random_song.random_song_start())
            elif choice == "10":
                print("正在停止所有功能...")
                audio_system.stop_function("super_idol")
                audio_system.stop_function("meow")
                audio_system.stop_function("bad_mic")
                audio_system.stop_function("virtual_out")
            elif choice == "0":
                print("程式結束")
                for name in ["super_idol", "meow", "bad_mic", "virtual_out"]:
                    audio_system.stop_function(name)
                break
            else:
                # 原有的選項處理邏輯
                if choice == "1":
                    audio_system.start_function("super_idol", super_idol.start_super())
                elif choice == "2":
                    audio_system.start_function("meow", meow.meow_start())
                elif choice == "3":
                    audio_system.start_function("bad_mic", bad_mic.bad_mic_start())
                elif choice == "4":
                    audio_system.start_function("virtual_out", random_song.random_song_start())
                elif choice == "5":
                    audio_system.stop_function("super_idol")
                elif choice == "6":
                    audio_system.stop_function("meow")
                elif choice == "7":
                    audio_system.stop_function("bad_mic")
                elif choice == "8":
                    audio_system.stop_function("virtual_out")
                else:
                    print("無效的選擇，請重試")
        except Exception as e:
            print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    show_menu()
