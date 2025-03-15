import pyaudio
import numpy as np
import soundfile as sf
import threading

# 🔹 設定參數
MIC_DEVICE_INDEX = 1  # 你的麥克風裝置索引 (可用 pyaudio.list_devices() 找)
VIRTUAL_CABLE_INDEX = 2  # 你的虛擬音訊裝置 (CABLE Input)
CHUNK = 1024
RATE = 44100  # 取樣率
CHANNELS = 1

# 🔹 初始化 PyAudio
p = pyaudio.PyAudio()

# 🔹 開啟麥克風輸入
mic_stream = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=MIC_DEVICE_INDEX,
    frames_per_buffer=CHUNK,
)

# 🔹 開啟虛擬音訊輸出
output_stream = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    output_device_index=VIRTUAL_CABLE_INDEX,
    frames_per_buffer=CHUNK,
)

# 🔹 載入 MP3 檔案
audio_data, samplerate = sf.read("sounds/Voicy_Rickroll.mp3", dtype="int16")
audio_index = 0

# 🔹 音訊處理函數
def audio_mixer():
    global audio_index
    while True:
        # 讀取麥克風數據
        mic_data = np.frombuffer(mic_stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

        # 讀取 MP3 音樂數據
        if audio_index + CHUNK < len(audio_data):
            music_data = audio_data[audio_index : audio_index + CHUNK]
            audio_index += CHUNK
        else:
            music_data = np.zeros(CHUNK, dtype=np.int16)  # 若音樂播放完，填充空白音訊

        # **混音 (50% 麥克風 + 50% 音樂)**
        mixed_audio = (mic_data * 0.5 + music_data * 0.5).astype(np.int16)

        # 發送到虛擬音訊輸出
        output_stream.write(mixed_audio.tobytes())

# 🔹 啟動混音執行緒
mixer_thread = threading.Thread(target=audio_mixer)
mixer_thread.start()
