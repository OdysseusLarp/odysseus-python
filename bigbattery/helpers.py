from time import sleep
from typing import Callable
from bigbattery.consts import NEOPIXEL_COUNT, EL_WIRE_PIN, NEOPIXEL_INTERNAL_BRIGHTNESS
import bigbattery.globals as globals
import random
import datetime


#### General helpers


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def arange(start: float, stop: float, step: float):
    """Yield numbers from start to stop by step, supporting floats and negative steps."""
    current = start
    if step > 0:
        while current < stop:
            yield round(current, 10)  # rounding to maintain precision
            current += step
    elif step < 0:
        while current > stop:
            yield round(current, 10)  # rounding to maintain precision
            current += step


#### Durationi helpers


def forever() -> bool:
    return True


def once() -> Callable[[], bool]:
    has_run = False

    def run_once():
        nonlocal has_run
        if has_run:
            return False
        has_run = True
        return True

    return run_once


def duration(seconds: float) -> Callable[[], bool]:
    end_at = datetime.datetime.now() + datetime.timedelta(seconds=seconds)

    def run_while():
        return datetime.datetime.now() < end_at

    return run_while
