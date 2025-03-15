import pygame
import time
import os
import random

pygame.mixer.init()
pygame.mixer.music.load("sounds/super-idol-de-xiao-rong-du-mei-ni-de-tian.mp3")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    time.sleep(1)

print("播放結束")
