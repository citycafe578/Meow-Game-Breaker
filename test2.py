import threading
import meow
import random_song
import super_idol
import bad_mic

class TestSystem:
    def __init__(self):
        self.threads = {}
        self.running = {}

    def start_function(self, name, func):
        if name not in self.running or not self.running[name]:
            thread = threading.Thread(target=func, daemon=True)
            self.threads[name] = thread
            self.running[name] = True
            thread.start()
            print(f"{name} 已啟動")
        else:
            print(f"{name} 已在運行中")

    def stop_function(self, name):
        if name in self.running and self.running[name]:
            # 停止功能的邏輯（如果需要）
            self.running[name] = False
            print(f"{name} 已停止")
        else:
            print(f"{name} 未在運行中")

def show_menu():
    test_system = TestSystem()

    while True:
        print("\n=== 測試選單 ===")
        print("1. 啟動 meow")
        print("2. 啟動 random_song")
        print("3. 啟動 super_idol")
        print("4. 啟動 bad_mic")
        print("5. 停止 meow")
        print("6. 停止 random_song")
        print("7. 停止 super_idol")
        print("8. 停止 bad_mic")
        print("0. 離開")
        
        choice = input("請選擇功能 (0-8): ")
        
        try:
            if choice == "1":
                test_system.start_function("meow", meow.meow_start)
            elif choice == "2":
                test_system.start_function("random_song", random_song.play_mp3)
            elif choice == "3":
                test_system.start_function("super_idol", super_idol.start_super)
            elif choice == "4":
                test_system.start_function("bad_mic", bad_mic.bad_mic_start)
            elif choice == "5":
                test_system.stop_function("meow")
            elif choice == "6":
                test_system.stop_function("random_song")
            elif choice == "7":
                test_system.stop_function("super_idol")
            elif choice == "8":
                test_system.stop_function("bad_mic")
            elif choice == "0":
                print("測試結束")
                for name in ["meow", "random_song", "super_idol", "bad_mic"]:
                    test_system.stop_function(name)
                break
            else:
                print("無效的選擇，請重試")
        except Exception as e:
            print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    show_menu()