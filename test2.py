import bad_mic, meow, random_song, super_idol
import threading

mic_thread = threading.Thread(target=bad_mic.bad_mic_start(), daemon=True)
mic_thread.start()

meow_thread = threading.Thread(target=meow.meow_start(), daemon=True)
meow_thread.start()