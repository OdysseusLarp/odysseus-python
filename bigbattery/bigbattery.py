from odysseus import log
from odysseus.taskbox import *
import random
from time import sleep
import board
import pwmio
import digitalio
import neopixel
import threading
from bigbattery.consts import (
    NEOPIXEL_COUNT,
    EL_WIRE_PIN,
    NEOPIXEL_PIN,
    NEOPIXEL_ORDER,
    NEOPIXEL_BRIGHTNESS,
    NEOPIXEL_INTERNAL_BRIGHTNESS,
)
import bigbattery.neopixel_animations as animations
from bigbattery.neopixel_animations import forever, duration, once
import bigbattery.globals as globals

# Usage:  python3 battery.py --id myid

# How often to run logic (in seconds)
RUN_INTERVAL = 1.0

default_state = {
    "capacity_percent": 100,
    "connected_position": 0,
    "brightness": 20,
}


def logic(state, backend_change):
    # Update connected_position
    state["connected_position"] = read_position()

    globals.capacity_percent = int(state["capacity_percent"])

    if animations.current_brightness() != state.get("brightness", NEOPIXEL_INTERNAL_BRIGHTNESS):
        print(f"Changing brightness from {animations.current_brightness()} to {state['brightness']}")
        animations.recalculate_gamma(state["brightness"])

    return state


def read_position():
    position_value = 0

    for i in range(len(location_pins)):
        # Pins use pull-up and are grounded when connected, thus "not"
        if not location_pins[i].value:
            position_value |= 1 << i

    return position_value


def update_charge_display(percentage):
    # TODO: Implement
    print("Charge: " + str(percentage) + "%")


# Pins that indicate where battery is connected. Each can be floating or grounded.
# These are converted to an int as bits, 0 = floating, 1 = GND.
# First pin in array is the least significant bit.
LOCATION_INPUT_PINS = [board.D4, board.D5, board.D6]
location_pins = []


def neopixel_animation_thread():
    #    animations.fade_test_animation(run_while=forever)
    # animations.capacity_display_animation(run_while=forever)
    while True:
        print("Jumping")
        animations.jump_static_animation(run_while=duration(10))
        print("Jump end")
        animations.jump_end_animation(run_while=once())
        print("Capacity")
        animations.capacity_display_animation(run_while=duration(10))
    print("Starting neopixel animation", globals.neopixels)
    animations.jump_end_animation(run_while=forever)


def box_init():
    print("INIT NEOPIXELS")
    globals.neopixels = neopixel.NeoPixel(
        NEOPIXEL_PIN,
        NEOPIXEL_COUNT,
        brightness=NEOPIXEL_BRIGHTNESS,
        auto_write=False,
        pixel_order=NEOPIXEL_ORDER,
    )

    el_wire = pwmio.PWMOut(EL_WIRE_PIN, frequency=5000, duty_cycle=0)

    # Initialize location pins
    for pin in LOCATION_INPUT_PINS:
        location_pins.append(digitalio.DigitalInOut(pin))
        location_pins[-1].direction = digitalio.Direction.INPUT
        location_pins[-1].pull = digitalio.Pull.UP

    # Start neopixel animation thread
    print("Starting neopixel animation thread")
    neopixel_thread = threading.Thread(target=neopixel_animation_thread)
    neopixel_thread.start()


options = {
    "init": box_init,
    "callback": logic,
    "run_interval": RUN_INTERVAL,
    "initial_state": default_state,
    # "write_interval": 2
    # "mock_init":box_init
}

TaskBoxRunner(options).run()
