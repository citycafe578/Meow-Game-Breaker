import pyaudio

p = pyaudio.PyAudio()

# 列出所有音訊裝置
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(f"裝置索引: {i} - 名稱: {dev['name']} - 類型: {dev['maxInputChannels']} 輸入 / {dev['maxOutputChannels']} 輸出")
    
p.terminate()
