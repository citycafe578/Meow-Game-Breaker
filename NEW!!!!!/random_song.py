import random
import time
from audio_manager import AudioManager

audio_manager = AudioManager()

def random_time():
    while True:
        time.sleep(random.randint(1, 10))  # 隨機等待 1 到 10 秒
        song_num = random.randint(1, 5)  # 隨機選擇 1 到 5 的歌曲編號
        audio_path = f"NEW!!!!!/sounds/{song_num}.mp3"
        audio_manager.play_audio(priority=2, audio_path=audio_path)  # 優先級設為 2