import sounddevice as sd
import numpy as np
import time
from pydub import AudioSegment

# 設定參數
FORMAT = 'int16'
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENCE_THRESHOLD = 8000  # 靜音判定閾值（越低越敏感）
SILENCE_DURATION = 0.75  # 多少秒靜音判斷為講話結束
MP3_FILE = "NEW!!!!!/sounds/3.mp3"  # 替換為你的音檔

def is_speaking(audio_data):
    volume = np.abs(audio_data).mean()
    return volume > SILENCE_THRESHOLD

def play_sound():
    audio = AudioSegment.from_file(MP3_FILE)
    samples = np.array(audio.get_array_of_samples())
    sd.play(samples, samplerate=audio.frame_rate)
    sd.wait()

def main():
    def callback(indata, frames, time, status):
        nonlocal silent_time, was_speaking
        if status:
            print(status)
        if is_speaking(indata):
            was_speaking = True
            silent_time = 0
        else:
            if was_speaking:
                silent_time += frames / RATE
                if silent_time >= SILENCE_DURATION:
                    print("Speech ended, playing sound...")
                    play_sound()
                    was_speaking = False
                    silent_time = 0

    silent_time = 0
    was_speaking = False

    with sd.InputStream(channels=CHANNELS, callback=callback, blocksize=CHUNK, samplerate=RATE):
        print("Listening...")
        while True:
            time.sleep(0.1)

def meow_start():
    main()