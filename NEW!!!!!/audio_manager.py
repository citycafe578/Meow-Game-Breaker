import threading
import queue
import sounddevice as sd
import numpy as np
from pydub import AudioSegment

class AudioManager:
    def __init__(self):
        self.audio_queue = queue.PriorityQueue()
        self.lock = threading.Lock()
        self.current_priority = None  # 當前正在播放的音效優先級
        self.playing = False

    def play_audio(self, priority, audio_path):
        """
        將音效請求加入佇列。如果優先級高於當前播放的音效，則立即播放。
        """
        with self.lock:
            # 如果新的音效優先級高於當前播放的音效，則停止當前音效
            if self.playing and (self.current_priority is None or priority < self.current_priority):
                print(f"停止當前音效，播放優先級更高的音效: {audio_path}")
                sd.stop()  # 停止當前音效
                self.playing = False

            # 將新的音效加入佇列
            self.audio_queue.put((priority, audio_path))
            self._process_queue()

    def _process_queue(self):
        """
        處理音效佇列，按優先級播放音效。
        """
        if self.playing:
            return  # 如果正在播放音效，直接返回

        if not self.audio_queue.empty():
            priority, audio_path = self.audio_queue.get()
            self.current_priority = priority
            self.playing = True
            threading.Thread(target=self._play_audio_thread, args=(audio_path,)).start()

    def _play_audio_thread(self, audio_path):
        """
        播放音效的執行緒。
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            samples = np.array(audio.get_array_of_samples())
            sd.play(samples, samplerate=audio.frame_rate)
            sd.wait()
        except Exception as e:
            print(f"播放音檔時發生錯誤: {e}")
        finally:
            with self.lock:
                self.playing = False
                self.current_priority = None
                self._process_queue()  # 播放下一個音效