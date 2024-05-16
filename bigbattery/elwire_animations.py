from typing import Callable
from time import sleep
import random
import bigbattery.globals as globals
from bigbattery.helpers import duration

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


CONNECT_ANIMATION = [
    # Start by blinking
    (0, 0.1),
    (10, 0.1),
    (0, 0.1),
    (8, 0.1),
    (0, 0.2),
    (10, 0.1),
    (0, 0.1),
    (10, 0.15),
    (0, 0.2),
    (10, 0.2),
    (6, 0.1),
    (10, 0.1),
    (2, 0.1),
    # Stabilize on
    (10, 0.1),
    (0, 0.1),
    (10, 0.3),
    (8, 0.1),
    (10, 0.2),
    (7, 0.1),
    (10, 3.7),
    # Start fading out while flickering
    (9, 1.5),
    (10, 0.1),
    (8, 2.3),
    (10, 0.1),
    (7, 1.7),
    (10, 0.1),
    (6, 0.2),
    (10, 0.1),
    (6, 0.8),
    (10, 0.1),
    (5, 2.3),
    (10, 0.1),
    (4, 1.9),
    (10, 0.1),
    (3, 0.4),
    (10, 0.1),
    (2, 2.3),
    (10, 0.1),
    (1, 3.5),
    (10, 0.1),
    (0, 0.5),
]

DISCONNECT_ANIMATION = [
    (10, 0.1),
    (0, 0.2),
    (10, 0.1),
    (5, 0.1),
    (8, 0.2),
    (3, 0.1),
    (10, 0.4),
    (7, 0.2),
    (10, 0.2),
    (5, 0.1),
    (10, 0.9),
    (9, 0.3),
    (8, 0.3),
    (7, 0.3),
    (6, 0.3),
    (5, 0.3),
    (4, 0.3),
    (3, 0.3),
    (2, 0.3),
    (1, 0.3),
    (0, 0.3),
]


def burn_in():
    """Initial burn-in animation. EL wire flickers initially so purge it out."""
    fade_in_out_animation(run_while=duration(3))
    globals.elwire.duty_cycle = 0
    sleep(1)


def play_animation(run_while: Callable[[], bool], animation: list[tuple[int, float]], loop: bool = False):
    while run_while():
        for level, duration in animation:
            print(level, duration)
            globals.elwire.duty_cycle = elwire_levels[level]
            sleep(duration)
            if not run_while():
                loop = False
                break
        if not loop:
            break


def connected_animation(run_while: Callable[[], bool], initial_animation: bool = True):
    """Animation to play when battery is connected."""
    if initial_animation:
        play_animation(run_while, CONNECT_ANIMATION, loop=False)
    while run_while():
        # Initial animation ends off, so delay first then flash
        t = random.uniform(0.1, 5)
        print("Sleep", t)
        sleep(t)
        globals.elwire.duty_cycle = elwire_levels[MAX_LEVEL]
        sleep(0.1)
        globals.elwire.duty_cycle = elwire_levels[0]


def disconnected_animation(run_while: Callable[[], bool]):
    play_animation(run_while, DISCONNECT_ANIMATION, loop=False)


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
