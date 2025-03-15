import pyaudio
import numpy as np
import pygame
import time

# 設定參數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENCE_THRESHOLD = 8000  # 靜音判定閾值（越低越敏感）
SILENCE_DURATION = 0.75  # 多少秒靜音判斷為講話結束
MP3_FILE = "sounds/meow.mp3"  # 替換為你的音檔

def is_speaking(audio_data):
    volume = np.abs(np.frombuffer(audio_data, dtype=np.int16)).mean()
    return volume > SILENCE_THRESHOLD

def play_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(MP3_FILE)
    pygame.mixer.music.play()
    time.sleep(1)  # 只播放 1 秒
    pygame.mixer.music.stop()

def main():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    input=True, frames_per_buffer=CHUNK)
    
    silent_time = 0
    was_speaking = False
    
    print("Listening...")
    while True:
        audio_data = stream.read(CHUNK, exception_on_overflow=False)
        if is_speaking(audio_data):
            was_speaking = True
            silent_time = 0
        else:
            if was_speaking:
                silent_time += CHUNK / RATE
                if silent_time >= SILENCE_DURATION:
                    print("Speech ended, playing sound...")
                    play_sound()
                    was_speaking = False  # 確保只播放一次
                    silent_time = 0
    
    stream.stop_stream()
    stream.close()
    p.terminate()

def meow_start():
    # if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     main()