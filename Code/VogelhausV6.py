import RPi.GPIO as GPIO
from time import sleep
from picamera2 import Picamera2, Preview
import pyaudio
import wave
from multiprocessing import Process
from datetime import datetime
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
SecondsOfRecording = 20

sensorPin = 23
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensorPin, GPIO.IN)

path = "/home/semi/Vogelhaus/"
hourBegin = 4
hourEnd = 22
NumberOfFirstPhotos = 2
NumberOfPhotosAfterwards = 1
TimeBetweenFirstPhotos = 1.5
TimeAfterBird = 15
checkTimeDay = 1
checkTimeNight = 20


def rightHour():
    currentTime = datetime.now()
    hour = int(currentTime.strftime('%H'))
    return hourBegin < hour < hourEnd


def getDatetime():
    currentTime = datetime.now()
    return currentTime.strftime('%y%m%d-%H%M%S')


def createFolder(formatedTime):
    folderName = f"{formatedTime}"
    os.makedirs(f"{path}{folderName}", exist_ok=True)
    print("Folder created!")
    return f"{path}{folderName}"


def takeFirstPhotos(formatedTime, PathWithFolder):
    print("Nimmt die ersten Fotos auf...")
    picam = Picamera2()
    config = picam.create_preview_configuration()
    picam.configure(config)
    picam.start()

    for i in range(NumberOfFirstPhotos):
        picam.capture_file(f"{PathWithFolder}/{formatedTime}_Foto{i + 1}.jpg")
        print(f"Photo {i + 1}")
        sleep(TimeBetweenFirstPhotos)

    picam.close()
    print("Die ersten Fotos aufgenommen und gespeichert!")


def recordAudio(formatedTime, PathWithFolder):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("Aufnahme wird gestartet...")
    frames = []
    for i in range(0, int(RATE / CHUNK * SecondsOfRecording)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(f"{PathWithFolder}/{formatedTime}_Audio.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Audio aufgenommen und gespeichert!")


def takePhotosAfterwards(formatedTime, PathWithFolder):
    print("Nimmt das letzte Fotos auf...")
    picam = Picamera2()
    config = picam.create_preview_configuration()
    picam.configure(config)
    picam.start()

    for i in range(NumberOfPhotosAfterwards):
        picam.capture_file(f"{PathWithFolder}/{formatedTime}_Foto{i + 1 + NumberOfFirstPhotos}.jpg")
        print(f"Photo {i + 1 + NumberOfFirstPhotos}")
        sleep(TimeBetweenFirstPhotos)

    picam.close()
    print("Alle Fotos aufgenommen und gespeichert!")


def convertAudio(PathWithFolder, formatedTime):
    print("Convert File...")
    os.system(f"ffmpeg -i {PathWithFolder}/{formatedTime}_Audio.wav -vn -ar 44100 -ac 2 -b:a 192k {PathWithFolder}/{formatedTime}_Audio.mp3")
    os.remove(f"{PathWithFolder}/{formatedTime}_Audio.wav")


def SaveError(error, formatedTime):
    with open(f"{path}Errors.txt", "a") as ErrorTxt:
        print(f"Error: {formatedTime}")
        ErrorTxt.write(f"Error: {formatedTime}\n")
        print(f"{error}")
        ErrorTxt.write(error)
        print(f"\n{66*"-"}\n\n")
        ErrorTxt.write(f"\n{66*"-"}\n\n")


def Vogelhaus():
    while True:
        try:
            movement = GPIO.input(sensorPin)  # output 0 or 1
            if movement == 1 and rightHour():

                print("Bewegung erkannt!")

                formatedTime = getDatetime()

                PathWithFolder = createFolder(formatedTime)

                takeFirstPhotos(formatedTime, PathWithFolder)

                recordAudio(formatedTime, PathWithFolder)

                takePhotosAfterwards(formatedTime, PathWithFolder)

                convertAudio(PathWithFolder, formatedTime)

                sleep(TimeAfterBird)

                movement = 0
                print("Bereit")

            else:
                if rightHour():
                    sleep(checkTimeDay)
                else:
                    print("Nacht")
                    sleep(checkTimeNight)

        except Exception as err:
            error = str(err)
            SaveError(error, formatedTime)
            Vogelhaus(formatedTime)
            movement = 0
            sleep(TimeAfterBird)
            return


Vogelhaus()
