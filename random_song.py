from pydub import AudioSegment
import pyaudio


VIRTUAL_AUDIO_DEVICE_NAME = "CABLE Input"

def get_device_index(device_name):
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_name in device_info["name"]:
            return i
    raise ValueError(f"找不到音訊設備: {device_name}")

def play_mp3_to_virtual_device(mp3_file, device_name):
    audio = AudioSegment.from_file(mp3_file)
    p = pyaudio.PyAudio()
    device_index = get_device_index(device_name)

    stream = p.open(format=p.get_format_from_width(audio.sample_width),
                    channels=audio.channels,
                    rate=audio.frame_rate,
                    output=True,
                    output_device_index=device_index)

    # 播放音訊
    print(f"正在播放 {mp3_file} 到虛擬音訊設備: {device_name}")
    chunk_size = 1024
    audio_data = audio.raw_data

    for i in range(0, len(audio_data), chunk_size):
        stream.write(audio_data[i:i + chunk_size])

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("播放完成")

def random_song_start():
    play_mp3_to_virtual_device("sounds/super.mp3", VIRTUAL_AUDIO_DEVICE_NAME)
