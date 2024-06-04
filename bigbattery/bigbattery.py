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
    LOCATION_INPUT_PINS,
    LOCATION_ENGINEERING,
    JUMP_EXIT_TIME,
)
import bigbattery.neopixel_animations as neopixel_animations
import bigbattery.elwire_animations as elwire_animations
from bigbattery.helpers import forever, duration, once
import bigbattery.globals as globals

# Usage:  python3 battery.py --id myid

# How often to run logic (in seconds)
RUN_INTERVAL = 1.0

default_state = {
    "capacity_percent": 100,
    "connected_position": 0,
    "brightness": 20,
    "active": False,
}

previous_connected_position = 0


def logic(state, backend_change):
    global previous_connected_position

    # Update connected_position in state if it has remained stable since last run
    current_connected_position = read_position()
    if previous_connected_position == current_connected_position:
        globals.connected_position = state["connected_position"] = current_connected_position
    previous_connected_position = current_connected_position

    # Update globals from state
    globals.is_active = state["active"]
    globals.capacity_percent = int(state["capacity_percent"])

    # Update charge display brightness if necessary
    if neopixel_animations.current_brightness() != state.get("brightness", NEOPIXEL_INTERNAL_BRIGHTNESS):
        print(f"Changing brightness from {neopixel_animations.current_brightness()} to {state['brightness']}")
        neopixel_animations.recalculate_gamma(state["brightness"])

    return state


location_pins = []


def read_position():
    """Read connected position from location pins."""
    position_value = 0

    for i in range(len(location_pins)):
        # Pins use pull-up and are grounded when connected, thus "not"
        if not location_pins[i].value:
            position_value |= 1 << i

    return position_value


### Animation helper functions
def has_charge() -> bool:
    return globals.capacity_percent > 0


def is_empty() -> bool:
    return globals.capacity_percent <= 0


def is_disconnected() -> bool:
    return globals.connected_position == 0


def is_connected_and_inactive_and_charged() -> bool:
    return globals.connected_position != 0 and not globals.is_active and has_charge()


def is_connected_and_active_and_charged() -> bool:
    return globals.connected_position != 0 and globals.is_active and has_charge()


### NEOPIXEL animation logic
def neopixel_animation_thread():
    """Background thread for running Neopixel animations based on global state."""
    # Show fade up/down to show LEDs work
    neopixel_animations.fade_up_down(delay=0.005, step=3)
    neopixel_animations.fade_up_down(delay=0.005, step=3)

    while True:
        if not has_charge():
            print("Neopixel: Capacity is zero")
            neopixel_animations.battery_empty_animation(run_while=is_empty)
        elif is_connected_and_inactive_and_charged() or is_disconnected():
            print("Neopixel: Capacity display")
            neopixel_animations.capacity_display_animation(
                run_while=lambda: is_connected_and_inactive_and_charged() or is_disconnected()
            )
        elif is_connected_and_active_and_charged():
            if globals.connected_position == LOCATION_ENGINEERING:
                print("Neopixel: Engineering jumping")
                neopixel_animations.jump_static_animation(run_while=is_connected_and_active_and_charged)
                # End animation
                neopixel_animations.jump_end_animation(run_while=once())
            else:
                # TODO: Other active displays
                neopixel_animations.capacity_display_animation(run_while=is_connected_and_active_and_charged)
        else:
            print(f"Neopixel: ERROR unknown state position={globals.connected_position} active={globals.is_active}")
            sleep(1)


### ELWIRE animation logic
def elwire_animation_thread():
    """Background thread for running EL wire animations based on global state."""
    # EL wire flickers initially, use burn-in animation to make it stable
    elwire_animations.burn_in()

    previous_connected = False
    while True:
        if not has_charge():
            print("elwire: Capacity is zero")
            elwire_animations.black_animation(run_while=is_empty)
            previous_connected = False
        elif is_disconnected():
            print("elwire: Disconnected")
            elwire_animations.disconnected_animation(run_while=is_disconnected)
            previous_connected = False
        elif is_connected_and_inactive_and_charged():
            print("elwire: Connected and inactive")
            elwire_animations.connected_animation(
                run_while=is_connected_and_inactive_and_charged,
                # Show initial animiation only if was previously disconnected
                initial_animation=(not previous_connected),
            )
            previous_connected = True
        elif is_connected_and_active_and_charged():
            if globals.connected_position == LOCATION_ENGINEERING:
                print("elwire: Engineering jumping")
                elwire_animations.static_animation(
                    run_while=is_connected_and_active_and_charged, rand_min=0.0, rand_max=0.3, flash_duration=0.05
                )
                # End animation duration should be approx same as neopixel_animations.jump_end_animation
                # i.e. JUMP_EXIT_TIME plus ~2s flashing
                elwire_animations.static_animation(
                    run_while=duration(JUMP_EXIT_TIME), rand_min=0.0, rand_max=0.15, flash_duration=0.05
                )
                elwire_animations.fade_in_out_animation(run_while=duration(2), sleep_time=0.02)
            else:
                # TODO: Other active displays
                elwire_animations.fade_in_out_animation(run_while=is_connected_and_active_and_charged, sleep_time=0.02)
            previous_connected = True
        else:
            print(f"elwire: ERROR unknown state position={globals.connected_position} active={globals.is_active}")
            sleep(1)


def box_init():
    print("INIT NEOPIXELS")
    globals.neopixels = neopixel.NeoPixel(
        NEOPIXEL_PIN,
        NEOPIXEL_COUNT,
        brightness=NEOPIXEL_BRIGHTNESS,
        auto_write=False,
        pixel_order=NEOPIXEL_ORDER,
    )

    globals.elwire = pwmio.PWMOut(EL_WIRE_PIN, frequency=500, duty_cycle=0)
    print(f"Initialized EL-wire PWM with frequency {globals.elwire.frequency}")

    # Initialize location pins
    for pin in LOCATION_INPUT_PINS:
        location_pins.append(digitalio.DigitalInOut(pin))
        location_pins[-1].direction = digitalio.Direction.INPUT
        location_pins[-1].pull = digitalio.Pull.UP

    # Start neopixel animation thread
    print("Starting neopixel animation thread")
    neopixel_thread = threading.Thread(target=neopixel_animation_thread)
    neopixel_thread.start()

    # Start EL wire animation thread
    print("Starting EL wire animation thread")
    elwire_thread = threading.Thread(target=elwire_animation_thread)
    elwire_thread.start()


options = {
    "init": box_init,
    "callback": logic,
    "run_interval": RUN_INTERVAL,
    "initial_state": default_state,
    # "write_interval": 2
    # "mock_init":box_init
}

TaskBoxRunner(options).run()
