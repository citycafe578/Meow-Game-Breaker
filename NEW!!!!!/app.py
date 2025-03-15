import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
from audio_utils import adjust_gain

class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音效調整工具")

        # 偵測音訊裝置
        self.input_devices = [device['name'] for device in sd.query_devices() if device['max_input_channels'] > 0]
        self.output_devices = [device['name'] for device in sd.query_devices() if device['max_output_channels'] > 0]

        # 預設增益值
        self.gain_db = tk.DoubleVar(value=0)

        # 音訊串流控制
        self.stream = None

        # 建立 GUI 元件
        self.create_widgets()

    def create_widgets(self):
        # 輸入裝置選單
        tk.Label(self.root, text="輸入裝置:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_device_combo = ttk.Combobox(self.root, values=self.input_devices, state="readonly")
        self.input_device_combo.grid(row=0, column=1, padx=10, pady=10)
        self.input_device_combo.current(0)

        # 輸出裝置選單
        tk.Label(self.root, text="輸出裝置:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_device_combo = ttk.Combobox(self.root, values=self.output_devices, state="readonly")
        self.output_device_combo.grid(row=1, column=1, padx=10, pady=10)
        self.output_device_combo.current(0)

        # 增益調整拉桿
        tk.Label(self.root, text="增益 (dB):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.gain_slider = tk.Scale(self.root, from_=-20, to=20, resolution=0.1, orient="horizontal", variable=self.gain_db)
        self.gain_slider.grid(row=2, column=1, padx=10, pady=10)

        # 開始按鈕
        self.start_button = tk.Button(self.root, text="開始", command=self.start_audio_stream)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=10)

        # 停止按鈕
        self.stop_button = tk.Button(self.root, text="停止", command=self.stop_audio_stream)
        self.stop_button.grid(row=4, column=0, columnspan=2, pady=10)

        # 離開按鈕
        self.exit_button = tk.Button(self.root, text="離開", command=self.root.quit)
        self.exit_button.grid(row=5, column=0, columnspan=2, pady=10)

    def audio_callback(self, indata, outdata, frames, time, status):
        """
        音訊處理回呼函式，用於即時調整增益並輸出音訊。
        """
        if status:
            print(f"狀態錯誤: {status}")
        # 調整增益
        audio_data = indata[:, 0]  # 單聲道處理
        adjusted_audio = adjust_gain(audio_data, self.gain_db.get())
        outdata[:, 0] = adjusted_audio  # 輸出調整後的音訊

    def start_audio_stream(self):
        """
        開始音訊串流。
        """
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
        """
        停止音訊串流。
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("音訊串流已停止")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioApp(root)
    root.mainloop()