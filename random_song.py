from pydub import AudioSegment
from pydub.playback import play
import pyaudio

# 設定虛擬音訊設備的名稱
VIRTUAL_AUDIO_DEVICE_NAME = "CABLE Input"  # 虛擬音訊設備名稱

# 找到虛擬音訊設備的索引
def get_device_index(device_name):
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_name in device_info["name"]:
            return i
    raise ValueError(f"找不到音訊設備: {device_name}")

# 播放 MP3 文件到虛擬音訊設備
def play_mp3_to_virtual_device(mp3_file, device_name):
    # 載入 MP3 文件
    audio = AudioSegment.from_file(mp3_file)

    # 初始化 PyAudio
    p = pyaudio.PyAudio()

    # 找到虛擬音訊設備的索引
    device_index = get_device_index(device_name)

    # 開啟音訊流
    stream = p.open(format=p.get_format_from_width(audio.sample_width),
                    channels=audio.channels,
                    rate=audio.frame_rate,
                    output=True,
                    output_device_index=device_index)

    # 播放音訊
    print(f"正在播放 {mp3_file} 到虛擬音訊設備: {device_name}")
    play(audio)  # 使用 pydub 的標準播放函式

    # 停止音訊流
    stream.stop_stream()
    stream.close()
    p.terminate()

# 播放 MP3 文件
def play_mp3():
    play_mp3_to_virtual_device("sounds/super.mp3", VIRTUAL_AUDIO_DEVICE_NAME)
