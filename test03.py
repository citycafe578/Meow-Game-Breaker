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

class AudioMaster:
    def __init__(self):
        self.app = None
        if not QApplication.instance():
            self.app = QApplication([])
        self.threads = {}
        self.running = {}
        self.VIRTUAL_AUDIO_DEVICE_NAME = "CABLE Input"
        
        # 初始化音訊參數
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.SILENCE_THRESHOLD = 8000
        self.SILENCE_DURATION = 0.75
        self.MEOW_FILE = "sounds/meow.wav"
        self.SUPER_FILE = "sounds/super.mp3"
        
        # 新增 bad_mic 相關變數
        self.gain = 5.0
        self.stream = None
        self.devices = self.get_audio_devices()
        self.timer = None
        
    # Super Idol 功能
    def detect_word_from_mic(self, target_words=["蘇", "書", "酥", "甦", "輸", "舒", "super", "Super"]):
        while self.running.get("super_idol", False):
            recognized = False
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                    audio = recognizer.listen(source, timeout=0.5)
                    text = recognizer.recognize_google(audio, language="zh-TW")
                    print(f"辨識結果: {text}")
                    detected_words = [word for word in target_words if word in text]
                    if detected_words:
                        self.play_sound(self.SUPER_FILE)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"語音服務錯誤: {e}")
                except Exception as e:
                    print(f"發生錯誤: {e}")

    # 喵喵功能
    def is_speaking(self, audio_data):
        volume = np.abs(np.frombuffer(audio_data, dtype=np.int16)).mean()
        return volume > self.SILENCE_THRESHOLD

    def meow_monitor(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=self.CHANNELS, 
                       rate=self.RATE, input=True, 
                       frames_per_buffer=self.CHUNK)
        
        silent_time = 0
        was_speaking = False
        
        while self.running.get("meow", False):
            audio_data = stream.read(self.CHUNK, exception_on_overflow=False)
            if self.is_speaking(audio_data):
                was_speaking = True
                silent_time = 0
            else:
                if was_speaking:
                    silent_time += self.CHUNK / self.RATE
                    if silent_time >= self.SILENCE_DURATION:
                        self.play_sound(self.MEOW_FILE)
                        was_speaking = False
                        silent_time = 0
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    # 音效播放功能
    def play_sound(self, sound_file):
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        time.sleep(1)
        pygame.mixer.music.stop()

    # 虛擬音訊輸出功能
    def play_virtual_device(self):
        while self.running.get("virtual_out", False):
            try:
                audio = AudioSegment.from_file(self.SUPER_FILE)
                p = pyaudio.PyAudio()  # 修正拼寫錯誤：PyAud9o -> PyAudio
                device_index = self.get_device_index()
                
                stream = p.open(
                    format=p.get_format_from_width(audio.sample_width),
                    channels=audio.channels,
                    rate=audio.frame_rate,
                    output=True,
                    output_device_index=device_index
                )
                
                chunk_size = 1024
                audio_data = audio.raw_data
                for i in range(0, len(audio_data), chunk_size):
                    if not self.running.get("virtual_out", False):
                        break
                    stream.write(audio_data[i:i + chunk_size])
                
                stream.stop_stream()
                stream.close()
                p.terminate()
            except Exception as e:
                print(f"虛擬音訊輸出錯誤: {e}")

    def get_device_index(self):
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if self.VIRTUAL_AUDIO_DEVICE_NAME in device_info["name"]:
                return i
        raise ValueError(f"找不到音訊設備: {self.VIRTUAL_AUDIO_DEVICE_NAME}")

    # 重新實作 bad_mic 功能
    def bad_mic_start(self):
        class BadMicWindow(QWidget):
            def __init__(self, parent=None):
                super().__init__()
                self.parent = parent
                self.initUI()
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update_gain_randomly)
                self.timer.start(2500)

            def initUI(self):
                self.setWindowTitle("Bad Mic")
                layout = QVBoxLayout()
                
                # 裝置選擇
                self.input_combo = QComboBox()
                self.output_combo = QComboBox()
                input_devices, output_devices = self.parent.devices
                
                for dev_id, dev_name, _ in input_devices:
                    self.input_combo.addItem(dev_name, dev_id)
                for dev_id, dev_name, _ in output_devices:
                    self.output_combo.addItem(dev_name, dev_id)
                    
                layout.addWidget(QLabel("輸入裝置:"))
                layout.addWidget(self.input_combo)
                layout.addWidget(QLabel("輸出裝置:"))
                layout.addWidget(self.output_combo)
                
                # Gain 控制
                self.gain_label = QLabel(f"Gain: {self.parent.gain}")
                self.gain_slider = QSlider(Qt.Orientation.Horizontal)  # 修正這裡
                self.gain_slider.setRange(0, 100)
                self.gain_slider.setValue(int(self.parent.gain * 10))
                self.gain_slider.valueChanged.connect(self.update_gain)
                
                layout.addWidget(self.gain_label)
                layout.addWidget(self.gain_slider)
                
                # 控制按鈕
                self.start_button = QPushButton("Start")
                self.stop_button = QPushButton("Stop")
                self.start_button.clicked.connect(self.start_audio)
                self.stop_button.clicked.connect(self.stop_audio)
                self.stop_button.setEnabled(False)
                
                layout.addWidget(self.start_button)
                layout.addWidget(self.stop_button)
                self.setLayout(layout)

            def update_gain(self):
                self.parent.gain = self.parent.time_setting()
                self.gain_label.setText(f"Gain: {self.parent.gain}")

            def update_gain_randomly(self):
                self.parent.gain = self.parent.time_setting()
                self.gain_label.setText(f"Gain: {self.parent.gain}")

            def start_audio(self):
                try:
                    input_device = self.input_combo.currentData()
                    output_device = self.output_combo.currentData()
                    
                    if input_device == -1:
                        input_device = sd.default.device[0]
                    if output_device == -1:
                        output_device = sd.default.device[1]
                    
                    self.parent.stream = sd.Stream(
                        device=(input_device, output_device),
                        samplerate=44100,
                        channels=(1, 1),
                        callback=self.parent.audio_callback,
                        blocksize=512
                    )
                    self.parent.stream.start()
                    self.start_button.setEnabled(False)
                    self.stop_button.setEnabled(True)
                    
                except Exception as e:
                    print(f"啟動串流時發生錯誤: {e}")
                    self.stop_audio()

            def stop_audio(self):
                if self.parent.stream:
                    self.parent.stream.stop()
                    self.parent.stream.close()
                    self.parent.stream = None
                    self.start_button.setEnabled(True)
                    self.stop_button.setEnabled(False)

            def closeEvent(self, event):
                self.stop_audio()
                event.accept()

        # 在主視窗中顯示 BadMic 視窗
        self.bad_mic_window = BadMicWindow(self)
        self.bad_mic_window.show()

    def get_audio_devices(self):
        input_devices = []
        output_devices = []
        try:
            input_devices.append((-1, "系統預設輸入", 'input'))
            output_devices.append((-1, "系統預設輸出", 'output'))
            
            for i, dev in enumerate(sd.query_devices()):
                try:
                    if dev['max_input_channels'] > 0:
                        input_devices.append((i, f"{dev['name']} (ID: {i})", 'input'))
                    if dev['max_output_channels'] > 0:
                        output_devices.append((i, f"{dev['name']} (ID: {i})", 'output'))
                except Exception as e:
                    print(f"跳過裝置 {i}: {e}")
        except Exception as e:
            print(f"無法取得裝置列表: {e}")
        return input_devices, output_devices

    def audio_callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        try:
            outdata[:] = indata * self.gain
        except Exception as e:
            print(f"音訊處理錯誤: {e}")
            outdata.fill(0)

    def time_setting(self):
        return 10 if random.randint(0, 1) == 1 else 0

    # 控制功能
    def start_function(self, name, func):
        if name not in self.running or not self.running[name]:
            self.running[name] = True
            thread = threading.Thread(target=func, daemon=True)
            self.threads[name] = thread
            thread.start()
            print(f"{name} 已啟動")
        else:
            print(f"{name} 已在運行中")
    
    def stop_function(self, name):
        if name in self.running and self.running[name]:
            self.running[name] = False
            if name in self.threads:
                self.threads[name].join(timeout=1)
            print(f"{name} 已停止")
        else:
            print(f"{name} 未在運行中")

if __name__ == "__main__":
    audio_master = AudioMaster()
    print("啟動所有功能...")
    
    try:
        # 設定並啟動Super idol功能
        audio_master.running["super_idol"] = True
        audio_master.start_function("super_idol", audio_master.detect_word_from_mic)
        print("Super idol已啟動")
        
        # 設定並啟動喵喵功能
        audio_master.running["meow"] = True
        audio_master.start_function("meow", audio_master.meow_monitor)
        print("喵喵功能已啟動")
        
        # 啟動麥克風干擾器
        audio_master.bad_mic_start()
        print("麥克風干擾器已啟動")
        
        # 設定並啟動虛擬音訊輸出
        audio_master.running["virtual_out"] = True
        audio_master.start_function("virtual_out", audio_master.play_virtual_device)
        print("虛擬音訊輸出已啟動")

        # Qt事件循環
        if audio_master.app:
            audio_master.app.exec()
        else:
            # 如果沒有Qt應用，使用簡單的循環保持程式運行
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n正在停止所有功能...")
        for name in list(audio_master.running.keys()):  # 使用list複製鍵值，避免在迭代時修改字典
            audio_master.stop_function(name)
        print("程式已結束")
    except Exception as e:
        print(f"執行時發生錯誤: {e}")
        raise e
