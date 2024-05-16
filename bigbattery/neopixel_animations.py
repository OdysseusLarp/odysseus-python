from time import sleep
from typing import Callable
from bigbattery.consts import NEOPIXEL_COUNT, EL_WIRE_PIN, NEOPIXEL_INTERNAL_BRIGHTNESS
import bigbattery.globals as globals
import random
from bigbattery.helpers import arange, clamp

#### Helpers

OFF = (0, 0, 0)


def scale_color(color: tuple[int, int, int], scale: float) -> tuple[int, int, int]:
    return (int(color[0] * scale), int(color[1] * scale), int(color[2] * scale))


def gamma_corrected_value(input_value, max_input=255, max_output=255, gamma=2.2, clamp_to_one=False):
    if clamp_to_one:
        if input_value == 0:
            return 0
        scaled_input = 1 + ((max_output - 1) * ((input_value / max_input) ** gamma))
    else:
        scaled_input = max_output * ((input_value / max_input) ** gamma)
    return min(round(scaled_input), max_output)


def current_brightness():
    return gamma_brightness


def recalculate_gamma(brightness: int):
    global gamma, gamma_brightness
    gamma = [gamma_corrected_value(i, max_output=brightness, clamp_to_one=True) for i in range(256)]
    gamma_brightness = brightness
    print(f"Set LED brightness to {brightness} and gamma table to {gamma}")


def apply_gamma(color: tuple[int, int, int]) -> tuple[int, int, int]:
    return (gamma[color[0]], gamma[color[1]], gamma[color[2]])


gamma_brightness = 0
gamma = []
recalculate_gamma(NEOPIXEL_INTERNAL_BRIGHTNESS)

#### RAINBOW COLOR WHEEL  (demo)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)


def rainbow_cycle_animation(run_while: Callable[[], bool]):
    while run_while():
        for j in range(255):
            for i in range(NEOPIXEL_COUNT):
                pixel_index = (i * 256 // NEOPIXEL_COUNT) + j
                globals.neopixels[i] = apply_gamma(wheel(pixel_index & 255))
            globals.neopixels.show()
            sleep(0.001)


def fade_test_animation(run_while: Callable[[], bool]):
    while run_while():
        for i in range(21):
            n = gamma[255 * i // 20]
            print(n)
            globals.neopixels[i] = (n, n, n)
        globals.neopixels.show()
        sleep(1)


#### REGULAR CAPACITY DISPLAY


def capacity_blinking_led(percent: int):
    return (NEOPIXEL_COUNT - 1) * min(percent, 99) // 100


def capacity_led_color(led: int):
    if led < 4:
        return (200, 0, 0)
    if led < 8:
        return (180, 150, 0)
    return (0, 180, 0)


def capacity_display(count: int):
    for i in range(NEOPIXEL_COUNT):
        if i < count:
            globals.neopixels[i] = apply_gamma(capacity_led_color(i))
        else:
            globals.neopixels[i] = (0, 0, 0)


def capacity_display_animation(run_while: Callable[[], bool]):
    while run_while():
        capacity = globals.capacity_percent
        blinking_led = capacity_blinking_led(capacity)
        capacity_display(blinking_led)
        globals.neopixels.show()

        blinking_led_color = capacity_led_color(blinking_led)
        for i in range(11):
            globals.neopixels[blinking_led] = apply_gamma(scale_color(blinking_led_color, i / 10))
            globals.neopixels.show()
            sleep(0.05)
        for i in range(10, 0, -1):
            globals.neopixels[blinking_led] = apply_gamma(scale_color(blinking_led_color, i / 10))
            globals.neopixels.show()
            sleep(0.05)
        globals.neopixels[blinking_led] = OFF
        globals.neopixels.show()
        sleep(0.2)


#### JUMP + JUMP END ANIMATIONS


def white_static(min_value=50, max_value=255):
    for i in range(NEOPIXEL_COUNT):
        n = random.randint(min_value, max_value)
        dr = random.randint(-10, 10)
        dg = random.randint(-10, 10)
        db = random.randint(-10, 10)
        r = gamma[clamp(n + dr, 0, 255)]
        g = gamma[clamp(n + dg, 0, 255)]
        b = gamma[clamp(n + db, 0, 255)]
        globals.neopixels[i] = (r, g, b)


def fade_up_down(delay: float = 0.01, step: int = 1):
    for i in range(0, 255, step):
        n = gamma[i]
        globals.neopixels.fill((n, n, n))
        globals.neopixels.show()
        sleep(delay)
    for i in range(255, -1, -step):
        n = gamma[i]
        globals.neopixels.fill((n, n, n))
        globals.neopixels.show()
        sleep(delay)


JUMP_STATIC_MIN_VALUE = 50
JUMP_STATIC_MAX_VALUE = 150


def jump_static_animation(run_while: Callable[[], bool]):
    """Animation during jump (static)"""
    while run_while():
        white_static(min_value=JUMP_STATIC_MIN_VALUE, max_value=JUMP_STATIC_MAX_VALUE)
        globals.neopixels.show()
        sleep(0.05)


def jump_end_animation(run_while: Callable[[], bool]):
    """Animation when exiting jump"""
    while run_while():
        # Static intensifies for 4 secs
        delays = list(arange(0.05, 0.005, -0.005))
        total_time = 4
        time_per_step = total_time / len(delays)
        min_value = JUMP_STATIC_MIN_VALUE
        max_value = JUMP_STATIC_MAX_VALUE
        for t in delays:
            min_value = max(min_value - 10, 1)
            max_value = min(max_value + 20, 255)
            # print("T", t)
            count = int(time_per_step / t)
            # print("COUNT", count, "")
            for i in range(count):
                white_static(min_value=min_value, max_value=max_value)
                globals.neopixels.show()
                sleep(t)

        # Face up+down several times
        fade_up_down(0.001, step=5)
        fade_up_down(0.001, step=5)
        fade_up_down(0.001, step=5)
        fade_up_down(0.001, step=5)
        fade_up_down(0.001, step=5)
        sleep(5)

        # Draw increasing capacity
        capacity = globals.capacity_percent
        blinking_led = capacity_blinking_led(capacity)
        for i in range(blinking_led):
            globals.neopixels[i] = apply_gamma(capacity_led_color(i))
            globals.neopixels.show()
            sleep(0.05)
