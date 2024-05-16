from typing import Callable
from time import sleep
import bigbattery.globals as globals

elwire_levels = [
    0,
    int(0.65 * 65535),
    int(0.70 * 65535),
    int(0.75 * 65535),
    int(0.80 * 65535),
    int(0.85 * 65535),
    int(0.90 * 65535),
    int(0.95 * 65535),
    int(0.97 * 65535),
    int(0.99 * 65535),
    int(1.00 * 65535),
]
MAX_LEVEL = len(elwire_levels) - 1
assert MAX_LEVEL == 10


def fade_in_out_animation(run_while: Callable[[], bool]):
    while run_while():
        for i in range(0, MAX_LEVEL + 1):
            print(i, elwire_levels[i])
            globals.elwire.duty_cycle = elwire_levels[i]
            sleep(0.1)
        for i in range(MAX_LEVEL - 1, 0, -1):
            print(i, elwire_levels[i])
            globals.elwire.duty_cycle = elwire_levels[i]
            sleep(0.1)


def blink_animation(run_while: Callable[[], bool]):
    while run_while():
        globals.elwire.duty_cycle = elwire_levels[MAX_LEVEL]
        sleep(0.5)
        globals.elwire.duty_cycle = elwire_levels[0]
        sleep(0.5)
