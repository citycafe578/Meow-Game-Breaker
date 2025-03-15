import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
from audio_utils import adjust_gain
from pydub import AudioSegment
import keyboard as kb
import random_song
import threading

class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音效調整工具")

        self.input_devices = [device['name'] for device in sd.query_devices() if device['max_input_channels'] > 0]
        self.output_devices = [device['name'] for device in sd.query_devices() if device['max_output_channels'] > 0]
        self.gain_db = tk.DoubleVar(value=0)
        self.stream = None
        self.is_streaming = False  # 狀態變數
        self.talk_key = None  # 綁定的按鍵
        self.key_options = [chr(i) for i in range(97, 123)]  # a-z
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="輸入裝置:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_device_combo = ttk.Combobox(self.root, values=self.input_devices, state="readonly")
        self.input_device_combo.grid(row=0, column=1, padx=10, pady=10)
        self.input_device_combo.current(0)

        tk.Label(self.root, text="輸出裝置:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_device_combo = ttk.Combobox(self.root, values=self.output_devices, state="readonly")
        self.output_device_combo.grid(row=1, column=1, padx=10, pady=10)
        self.output_device_combo.current(0)

        # 增益調整拉桿
        tk.Label(self.root, text="增益 (dB):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.gain_slider = tk.Scale(self.root, from_=-20, to=50, resolution=0.1, orient="horizontal", variable=self.gain_db)
        self.gain_slider.grid(row=2, column=1, padx=10, pady=10)
        
        # 按鍵綁定
        tk.Label(self.root, text="按鍵綁定:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.keybind_combo = ttk.Combobox(self.root, values=self.key_options, state="readonly")  # 下拉式選單
        self.keybind_combo.grid(row=3, column=1, padx=10, pady=10)
        self.keybind_combo.current(0)  # 預設選擇第一個按鍵

        # 開始/停止按鈕
        self.toggle_button = tk.Button(self.root, text="開始", command=self.toggle_audio_stream)
        self.toggle_button.grid(row=4, column=0, columnspan=2, pady=10)

        # 離開按鈕
        self.exit_button = tk.Button(self.root, text="離開", command=self.root.quit)
        self.exit_button.grid(row=5, column=0, columnspan=2, pady=10)

    def apply_distortion(self, audio_data, gain=1.0, threshold=0.5):
        """
        應用失真效果
        """
        audio_data = audio_data * gain
        audio_data = np.clip(audio_data, -threshold, threshold)
        return audio_data

    def play_sound(self):
        audio = AudioSegment.from_file("NEW!!!!!/sounds/meow.mp3")
        samples = np.array(audio.get_array_of_samples())
        sd.play(samples, samplerate=audio.frame_rate)
        sd.wait()

    def audio_callback(self, indata, outdata, frames, time, status):
        """
        音訊處理回呼函式，用於即時調整增益並輸出音訊。
        """
        if status:
            print(f"狀態錯誤: {status}")
        
        # 偵測是否按下 talk_key
        if self.talk_key and kb.is_pressed(self.talk_key):
            print("按下 talk_key")
            # 調整增益
            audio_data = indata[:, 0]  # 單聲道處理
            adjusted_audio = adjust_gain(audio_data, self.gain_db.get())
            # 應用失真效果
            distorted_audio = self.apply_distortion(adjusted_audio, gain=2.0, threshold=0.5)
            outdata[:] = distorted_audio.reshape(-1, 1)
        else:
            # 如果按鍵未按下，將輸出設為靜音
            outdata.fill(0)

    def start_audio_stream(self):
        input_device = self.input_device_combo.get()
        output_device = self.output_device_combo.get()

        # 找到裝置索引
        input_device_index = next(i for i, d in enumerate(sd.query_devices()) if d['name'] == input_device)
        output_device_index = next(i for i, d in enumerate(sd.query_devices()) if d['name'] == output_device)

        # 開啟音訊串流
        try:
            self.stream = sd.Stream(
                device=(input_device_index, output_device_index),
                samplerate=44100,
                channels=1,  # 單聲道
                dtype='float32',
                callback=self.audio_callback
            )
            self.stream.start()
            print("音訊串流已啟動")
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
            self.toggle_button.config(text="開始")
        else:
            self.talk_key = self.keybind_combo.get()  # 獲取綁定的按鍵
            self.start_audio_stream()
            self.toggle_button.config(text="停止")
        self.is_streaming = not self.is_streaming


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioApp(root)

    # 啟動隨機播放音樂的執行緒
    random_song_thread = threading.Thread(target=random_song.random_time)
    random_song_thread.daemon = True  # 設為守護執行緒，主程式結束時自動結束
    random_song_thread.start()

    root.mainloop()