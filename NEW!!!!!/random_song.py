import random
import time
from audio_manager import AudioManager
import sounddevice as sd

audio_manager = AudioManager()

def random_time():
    while True:

        time.sleep(random.randint(1, 10))  # 隨機等待 1 到 10 秒
        song_num = random.randint(1, 7)  # 隨機選擇 1 到 5 的歌曲編號
        audio_path = f"NEW!!!!!/sounds/{song_num}.mp3"
        print(f"Playing song: {audio_path}")
        audio_manager.play_audio(priority=1, audio_path=audio_path)  # 優先級設為 1
        print("Random song is running...")
        sd.wait()  # 等待音樂播放完成