from time import sleep
import os
from datetime import datetime

def getDatetime():
    currentTime = datetime.now()
    return currentTime.strftime('%y%m%d-%H%M%S')

while True:
    with open(f"/home/semi/Logs.txt", "a") as Logs:
        print(getDatetime())
        Logs.write(getDatetime()+"\n")
    sleep(5)
