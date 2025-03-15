import time
import shutil
import os
from PIL import Image
import pytesseract
from langdetect import detect_langs
import pyscreenshot as ImageGrab

if os.path.exists("images"):
    shutil.rmtree("images")
os.mkdir("images")

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

while True:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"images/screenshot_{timestamp}.png"
    ImageGrab.grab(bbox=(10, 400, 370, 560)).save(screenshot_path)
    img = Image.open(screenshot_path)
    text = pytesseract.image_to_string(img, lang="eng+chi_sim+chi_tra+jpn+rus")
    
    print(f"提取文字: {text}")
    if text.strip():
        try:
            detected_languages = detect_langs(text)
            print(f"檔案: {screenshot_path}")
            print("偵測語言:")
            for lang in detected_languages:
                print(f"語言: {lang.lang}, 機率: {lang.prob:.2f}")
        except Exception as e:
            print(f"無法偵測語言: {e}")
    else:
        print(f"檔案: {screenshot_path} 中無法提取文字")

    time.sleep(5)
