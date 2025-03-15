import pyaudio
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import threading

# 設定參數
FORMAT = pyaudio.paInt16  # 16-bit 音訊格式
CHANNELS = 1             # 單聲道
RATE = 44100             # 取樣率 (44.1 kHz)
CHUNK = 1024             # 每次讀取的音訊塊大小

# 載入 MP3 音樂
music = AudioSegment.from_file("sounds/Voicy_Rickroll.mp3")
music = music.set_frame_rate(RATE).set_channels(CHANNELS)

# 初始化 PyAudio
audio = pyaudio.PyAudio()

# 開啟麥克風錄製流
mic_stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

# 開啟音訊播放流
output_stream = audio.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           output=True)

# 混音函數
def mix_audio():
    global music
    music_index = 0
    music_data = np.array(music.get_array_of_samples(), dtype=np.int16)

    while True:
        # 從麥克風讀取音訊
        mic_data = mic_stream.read(CHUNK)
        mic_array = np.frombuffer(mic_data, dtype=np.int16)

        # 從音樂中提取對應的片段
        if music_index + CHUNK < len(music_data):
            music_chunk = music_data[music_index:music_index + CHUNK]
            music_index += CHUNK
        else:
            music_chunk = np.zeros(CHUNK, dtype=np.int16)  # 音樂結束後填充空白

        # 混音 (50% 麥克風 + 50% 音樂)
        mixed_audio = (mic_array * 0.5 + music_chunk * 0.5).astype(np.int16)

        # 播放混音後的音訊
        output_stream.write(mixed_audio.tobytes())

# 啟動混音執行緒
mix_thread = threading.Thread(target=mix_audio)
mix_thread.start()

print("音訊混音正在運行... 按下 Ctrl+C 停止")

try:
    while True:
        pass  # 持續運行，直到使用者中斷程式
except KeyboardInterrupt:
    print("程式已停止")
    mic_stream.stop_stream()
    mic_stream.close()
    output_stream.stop_stream()
    output_stream.close()
    audio.terminate()
