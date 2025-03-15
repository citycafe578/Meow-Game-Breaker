import sounddevice as sd
import numpy as np

def adjust_gain(audio_data, gain_db):
    """
    調整音效的增益。
    :param audio_data: numpy array，音效資料
    :param gain_db: float，增益值（分貝）
    :return: numpy array，調整後的音效資料
    """
    gain_factor = 10 ** (gain_db / 20)
    return np.clip(audio_data * gain_factor, -1.0, 1.0)

def play_audio(audio_data, sample_rate):
    """
    撥放音效。
    :param audio_data: numpy array，音效資料
    :param sample_rate: int，取樣率
    """
    # 撥放音效
    sd.play(audio_data, samplerate=sample_rate)
    sd.wait()