import random as r
import time as t
from pynput.keyboard import Key, Controller

keyboard = Controller()


class StopWatch:
    def __init__(self, hour, minute, second):
        self.t = (hour * 3600) + (minute * 60) + second

    def subtractTime(self, seconds):
        if self.t > 0:
            self.t -= seconds
        else:
            self.t = 0

    def isTimeOver(self):
        if self.t <= 0:
            return True
        else:
            return False

    def printTime(self):
        hour, minute = divmod(self.t, 3600)
        minute, second = divmod(minute, 60)
        return '{:02d}:{:02d}:{:02d}'.format(hour, minute, second)

    def time(self):
        return self.t


def enterCommand(command, waitTime):
    wait(r.randint(waitTime - 1, waitTime + 1))
    keyboard.type(command)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)


def wait(time):
    t.sleep(time)


def runArenaTraining():
    enterCommand(command='f/a', waitTime=6)
    enterCommand(command='f/8', waitTime=5)
    enterCommand(command='f/1', waitTime=5)


def runArenaPve(difficulty, attacks):
    enterCommand(command='f/a', waitTime=8)
    enterCommand(command='f/8', waitTime=6)
    enterCommand(command='f/5', waitTime=6)
    enterCommand(command='f/' + str(difficulty), waitTime=5)

    for a in range(attacks):
        enterCommand(command='f/1', waitTime=5)


interval = 10
hourly = StopWatch(0, 0, 10)

print("Hour: " + hourly.printTime())

while True:
    actionPoints = 19
    wait(interval)
    hourly.subtractTime(interval)

    if hourly.isTimeOver():
        for x in range(actionPoints):
            # runArenaTraining()
            runArenaPve(difficulty=10, attacks=8)
        hourly = StopWatch(1, 0, 0)

    print("Hour: " + hourly.printTime())
