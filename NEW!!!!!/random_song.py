import random
import time
import sounddevice as sd
import numpy as np
from pydub import AudioSegment

def random_time():
    while True:
        time.sleep(random.randint(1, 10))  # 隨機等待 1 到 10 秒
        song_num = random.randint(1, 5)  # 隨機選擇 1 到 5 的歌曲編號
        audio_path = f"NEW!!!!!/sounds/f{song_num}.mp3"  # 使用 f-string 格式化路徑
        try:
            audio = AudioSegment.from_file(audio_path)
            samples = np.array(audio.get_array_of_samples())
            sd.play(samples, samplerate=audio.frame_rate)
            sd.wait()
        except Exception as e:
            print(f"播放音檔時發生錯誤: {e}")