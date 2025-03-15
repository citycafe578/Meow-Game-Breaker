import sys
import pyaudio
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, 
                             QComboBox, QPushButton, QVBoxLayout)
from PyQt6.QtCore import Qt

class AudioProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Processor")

        self.label = QLabel("Select Input Device:")
        self.device_dropdown = QComboBox()
        self.devices = self.get_audio_devices()
        self.device_names = [d['name'] for d in self.devices]
        self.device_dropdown.addItems(self.device_names)

        self.process_button = QPushButton("Start Processing")
        self.process_button.clicked.connect(self.start_processing)

        self.stop_button = QPushButton("Stop Processing")
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)

        self.is_processing = False
        self.stream = None

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.device_dropdown)
        layout.addWidget(self.process_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def get_audio_devices(self):
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        devices = []
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_info = p.get_device_info_by_host_api_device_index(0, i)
                devices.append(device_info)
        p.terminate()
        return devices

    def start_processing(self):
        if not self.is_processing:
            self.is_processing = True
            self.process_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.start_audio_stream()

    def stop_processing(self):
        if self.is_processing:
            self.is_processing = False
            self.process_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.stop_audio_stream()

    def audio_callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        # 音訊處理範例：簡單的音量調整
        outdata[:] = indata * 2  # 將音量放大兩倍

    def start_audio_stream(self):
        device_name = self.device_dropdown.currentText()
        device_index = self.device_names.index(device_name)
        device = self.devices[device_index]
        
        samplerate = int(device['defaultSampleRate'])
        channels = device['maxInputChannels']

        try:
            self.stream = sd.Stream(samplerate=samplerate, 
                                    channels=channels, 
                                    callback=self.audio_callback)
            self.stream.start()
        except Exception as e:
            print(f"Error starting audio stream: {e}")

    def stop_audio_stream(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AudioProcessorApp()
    ex.show()
    sys.exit(app.exec())
