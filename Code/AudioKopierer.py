import shutil
import os

directories = os.listdir('G:\AlleOrdner')

for d in directories:
    shutil.copyfile(f'G:\AlleOrdner\{d}\{d}_Audio.mp3', f'G:\AlleAudios\{d}_Audio.mp3')
