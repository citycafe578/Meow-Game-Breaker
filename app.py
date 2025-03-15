import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from bad_mic import bad_mic_start
from meow import meow_start
from super_idol import start_super

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("音效整合器")
        self.setGeometry(100, 100, 400, 300)

        # 建立主要 widget 和垂直布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 建立按鈕
        bad_mic_btn = QPushButton("啟動麥克風干擾器")
        meow_btn = QPushButton("啟動貓叫聲")
        super_idol_btn = QPushButton("啟動 Super Idol")

        # 將按鈕加入布局
        layout.addWidget(bad_mic_btn)
        layout.addWidget(meow_btn)
        layout.addWidget(super_idol_btn)

        # 連接按鈕事件
        bad_mic_btn.clicked.connect(bad_mic_start)
        meow_btn.clicked.connect(meow_start)
        super_idol_btn.clicked.connect(start_super())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
