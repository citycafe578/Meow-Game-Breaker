import customtkinter as ctk
from tkinter import ttk
import sounddevice as sd
import numpy as np
from audio_utils import adjust_gain
from pydub import AudioSegment
import keyboard as kb
import random_song
import threading
import su
from audio_manager import AudioManager
import queue
import os
import meow  # 新增這行

class AudioManager:
    def play_audio(self, priority, audio_path):
        try:
            audio = AudioSegment.from_file(audio_path)
            samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
            sd.play(samples, samplerate=audio.frame_rate)
            sd.wait()  # 等待音效播放完成
            print(f"Playing audio: {audio_path}")
        except Exception as e:
            print(f"Error playing audio: {e}")

class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音效調整工具")

        self.input_devices = [device['name'] for device in sd.query_devices() if device['max_input_channels'] > 0]
        self.output_devices = [device['name'] for device in sd.query_devices() if device['max_output_channels'] > 0]
        self.gain_db = ctk.DoubleVar(value=0)
        self.stream = None
        self.is_streaming = False  # 狀態變數
        self.talk_key = None  # 綁定的按鍵
        self.key_options = [chr(i) for i in range(97, 123)]  # a-z
        self.was_talking = False  # 是否正在說話
        self.sound_queue = queue.Queue()  # 儲存音效數據

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self.root, text="輸入裝置:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_device_combo = ctk.CTkComboBox(self.root, values=self.input_devices, state="readonly")
        self.input_device_combo.grid(row=0, column=1, padx=10, pady=10)
        self.input_device_combo.set(self.input_devices[0])

        ctk.CTkLabel(self.root, text="輸出裝置:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_device_combo = ctk.CTkComboBox(self.root, values=self.output_devices, state="readonly")
        self.output_device_combo.grid(row=1, column=1, padx=10, pady=10)
        self.output_device_combo.set(self.output_devices[0])

        # 增益調整拉桿
        ctk.CTkLabel(self.root, text="增益 (dB):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.gain_slider = ctk.CTkSlider(self.root, from_=-20, to=50, number_of_steps=700, variable=self.gain_db)
        self.gain_slider.grid(row=2, column=1, padx=10, pady=10)

        # 按鍵綁定
        ctk.CTkLabel(self.root, text="按鍵綁定:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.keybind_combo = ttk.Combobox(self.root, values=self.key_options, state="readonly")  # 下拉式選單
        self.keybind_combo.grid(row=3, column=1, padx=10, pady=10)
        self.keybind_combo.current(0)  # 預設選擇第一個按鍵

        # 開始/停止按鈕
        self.toggle_button = ctk.CTkButton(self.root, text="開始", command=self.toggle_audio_stream)
        self.toggle_button.grid(row=4, column=0, columnspan=2, pady=10)

        # 離開按鈕
        self.exit_button = ctk.CTkButton(self.root, text="離開", command=self.root.quit)
        self.exit_button.grid(row=5, column=0, columnspan=2, pady=10)

    def apply_distortion(self, audio_data, gain=3.0, threshold=0.3):
        """ 應用失真效果 """
        audio_data = audio_data * gain
        return np.clip(audio_data, -threshold, threshold)

    def play_sound(self, file_path):
        """ 播放音效並加入音訊串流 """
        if not os.path.exists(file_path):
            print(f"錯誤: 找不到音效檔案 {file_path}")
            return

        try:
            audio = AudioSegment.from_file(file_path)
            samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
            self.sound_queue.put(samples)  # 將音效加入佇列
            sd.play(samples, samplerate=audio.frame_rate)  # 在本地播放音效
            print(f"播放音效: {file_path}")
        except Exception as e:
            print(f"播放音效時發生錯誤: {e}")

    def audio_callback(self, indata, outdata, frames, time, status):
        """ 音訊處理回呼函式，合併麥克風輸入與音效 """
        if status:
            print(f"狀態錯誤: {status}")

        # 處理麥克風輸入
        mic_audio = indata[:, 0]  # 單聲道
        mic_audio = adjust_gain(mic_audio, self.gain_db.get())
        mic_audio = self.apply_distortion(mic_audio)

        # 播放音效（若佇列有音效）
        if not self.sound_queue.empty():
            sound_audio = self.sound_queue.get()
            # 確保音效長度與 frames 一致
            if len(sound_audio) < len(mic_audio):
                sound_audio = np.pad(sound_audio, (0, len(mic_audio) - len(sound_audio)), mode='constant')
            elif len(sound_audio) > len(mic_audio):
                sound_audio = sound_audio[:len(mic_audio)]
        else:
            sound_audio = np.zeros_like(mic_audio)

        # 合併麥克風音訊與音效
        combined_audio = mic_audio + sound_audio
        combined_audio = np.clip(combined_audio, -1.0, 1.0)  # 避免溢出

        outdata[:] = combined_audio.reshape(-1, 1)

    def on_key_pressed(self):
        """ 當綁定按鍵被按下時 """
        self.was_talking = True

    def on_key_released(self):
        """ 當綁定按鍵被放開時，播放音效 """
        if self.was_talking:
            self.was_talking = False
            self.play_sound("NEW!!!!!/sounds/3.mp3")

    def start_audio_stream(self):
        input_device = self.input_device_combo.get()
        output_device = self.output_device_combo.get()

        input_device_index = next(i for i, d in enumerate(sd.query_devices()) if d['name'] == input_device)
        output_device_index = next(i for i, d in enumerate(sd.query_devices()) if d['name'] == output_device)

        try:
            # 使用音訊檔案的取樣率
            audio_path = "NEW!!!!!/sounds/1.mp3"  # 假設音訊檔案的取樣率是固定的
            audio = AudioSegment.from_file(audio_path)
            sample_rate = audio.frame_rate

            self.stream = sd.Stream(
                device=(input_device_index, output_device_index),
                samplerate=sample_rate,
                channels=1,  # 單聲道
                dtype='float32',
                callback=self.audio_callback
            )
            self.stream.start()
            print("音訊串流已啟動")

            self.talk_key = self.keybind_combo.get()
            kb.add_hotkey(self.talk_key, self.on_key_pressed)
            kb.add_hotkey(self.talk_key, self.on_key_released, trigger_on_release=True)

        except Exception as e:
            print(f"發生錯誤: {e}")

    def stop_audio_stream(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("音訊串流已停止")

    def toggle_audio_stream(self):
        if self.is_streaming:
            self.stop_audio_stream()
            self.toggle_button.configure(text="開始")
        else:
            self.start_audio_stream()
            self.toggle_button.configure(text="停止")
        self.is_streaming = not self.is_streaming

if __name__ == "__main__":
    root = ctk.CTk()
    app = AudioApp(root)

    # 啟動 meow 檢測的執行緒
    meow_thread = threading.Thread(target=meow.meow_start)
    meow_thread.daemon = True
    meow_thread.start()

    # 啟動隨機播放音樂的執行緒
    random_song_thread = threading.Thread(target=random_song.random_time)
    random_song_thread.daemon = True
    random_song_thread.start()

    # 啟動 su 語音辨識的執行緒
    su_thread = threading.Thread(target=su.start_super, args=(["蘇", "書", "酥", "甦", "輸", "舒", "super", "Super"],))
    su_thread.daemon = True
    su_thread.start()

    root.mainloop()
