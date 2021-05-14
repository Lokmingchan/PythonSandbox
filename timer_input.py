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


def enterCommand(command):
    keyboard.type(command)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)


daily = StopWatch(24, 0, 0)
hourly = StopWatch(1, 0, 0)
pve = StopWatch(3, 0, 0)
dungeon = StopWatch(12, 0, 0)
countdown = StopWatch(0, 25, 0)

print("Day: " + daily.printTime() + " | Hour: " + hourly.printTime() + " | PVE: " + pve.printTime() + " | Dungeon: " + dungeon.printTime() + " | CD: " + countdown.printTime())

while True:
    interval = 10
    t.sleep(interval)

    daily.subtractTime(interval)
    hourly.subtractTime(interval)
    pve.subtractTime(interval)
    dungeon.subtractTime(interval)
    countdown.subtractTime(interval)

    if daily.isTimeOver():
        enterCommand('a!daily')
        daily = StopWatch(24, r.randint(3, 15), r.randint(1, 59))

    if hourly.isTimeOver():
        enterCommand('a!hr')
        hourly = StopWatch(1, 0, r.randint(1, 59))

    if dungeon.isTimeOver() and pve.time() < 1800:
        keyboard.type('a!dungeon y')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        dungeon = StopWatch(12, 0, r.randint(1, 59))
        pve = StopWatch(3, 00, r.randint(1, 59))
    elif pve.isTimeOver() and dungeon.time() > 7200:
        keyboard.type('a!pve 3')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        pve = StopWatch(2, r.randint(40, 59), r.randint(1, 59))

    if countdown.isTimeOver():
        keyboard.type('a!cd')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        countdown = StopWatch(0, r.randint(25, 45), r.randint(1, 59))

    print("Day: " + daily.printTime() + " | Hour: " + hourly.printTime() + " | PVE: " + pve.printTime() + " | Dungeon: " + dungeon.printTime() + " | CD: " + countdown.printTime())


