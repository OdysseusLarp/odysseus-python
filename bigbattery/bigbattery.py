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
    LOCATION_MEDBAY,
    LOCATION_SCIENCE,
    LOCATION_FIGHTER1,
    LOCATION_FIGHTER2,
    LOCATION_FIGHTER3,
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
    "active": False,
    "brightness": 20,
    "led_rotation": 12,
}

previous_connected_position = 0


def logic(state, backend_change):
    global previous_connected_position

    # Update connected_position in state if it has remained stable since last run OR disconnected
    current_connected_position = read_position()
    if previous_connected_position == current_connected_position or current_connected_position == 0:
        globals.connected_position = state["connected_position"] = current_connected_position
    previous_connected_position = current_connected_position

    # Update globals from state
    globals.is_active = state["active"]
    globals.capacity_percent = int(state["capacity_percent"])
    globals.led_rotation = state["led_rotation"]

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


def is_active() -> bool:
    return globals.is_active


def is_disconnected() -> bool:
    return globals.connected_position == 0


def is_connected_and_inactive_and_charged() -> bool:
    return globals.connected_position != 0 and not globals.is_active and has_charge()


def is_connected_and_active_and_charged() -> bool:
    return globals.connected_position != 0 and globals.is_active and has_charge()


def is_jumping() -> bool:
    """Check whether is connected in enginerring room while jumping."""
    return globals.connected_position == LOCATION_ENGINEERING and globals.is_active


### NEOPIXEL animation logic
def neopixel_animation_thread():
    """Background thread for running Neopixel animations based on global state."""
    # Show fade up/down to show LEDs work
    neopixel_animations.fade_up_down(delay=0.005, step=3)
    neopixel_animations.fade_up_down(delay=0.005, step=3)

    while True:
        if is_jumping():
            # Engineering jump view overrides all others
            print("Neopixel: Engineering jumping")
            neopixel_animations.jump_static_animation(run_while=is_jumping)
            neopixel_animations.jump_end_animation(run_while=once())
        elif not has_charge():
            print("Neopixel: Capacity is zero")
            neopixel_animations.battery_empty_animation(run_while=lambda: is_empty() and not is_jumping())
        elif is_connected_and_inactive_and_charged() or is_disconnected():
            print("Neopixel: Capacity display")
            neopixel_animations.capacity_display_animation(
                run_while=lambda: is_connected_and_inactive_and_charged() or is_disconnected()
            )
        elif is_connected_and_active_and_charged():
            # TODO: Customize active displays (other than engineering)
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
        if is_jumping():
            # Engineering jump view overrides all others
            print("elwire: Engineering jumping")
            elwire_animations.static_animation(run_while=is_jumping, rand_min=0.0, rand_max=0.2, flash_duration=0.05)
            # End animation duration should be approx same as neopixel_animations.jump_end_animation
            # i.e. JUMP_EXIT_TIME plus ~2s flashing
            elwire_animations.static_animation(
                run_while=duration(JUMP_EXIT_TIME), rand_min=0.0, rand_max=0.1, flash_duration=0.05
            )
            elwire_animations.fade_in_out_animation(run_while=duration(2), sleep_time=0.02)
        elif not has_charge():
            print("elwire: Capacity is zero")
            elwire_animations.black_animation(run_while=lambda: is_empty() and not is_jumping())
            previous_connected = globals.connected_position != 0
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
            if globals.connected_position == LOCATION_MEDBAY:
                # Medbbay pulsates actively (short duration)
                print("elwire: Medbay active")
                elwire_animations.fade_in_out_animation(run_while=is_connected_and_active_and_charged, sleep_time=0.02)
            elif (
                globals.connected_position == LOCATION_FIGHTER1
                or globals.connected_position == LOCATION_FIGHTER2
                or globals.connected_position == LOCATION_FIGHTER3
            ):
                # Fighter jumpstart pulsates very fast (short duration)
                print("elwire: Fighter jumpstart active")
                elwire_animations.fade_in_out_animation(
                    run_while=is_connected_and_active_and_charged, sleep_time=0.02, step=3
                )
            elif globals.connected_position == LOCATION_SCIENCE:
                # Science room is static noise (relatively long duration)
                print("elwire: Science active")
                elwire_animations.static_animation(
                    run_while=is_connected_and_active_and_charged, rand_min=0.0, rand_max=0.5, flash_duration=0.05
                )
            else:
                # Default active display
                print("elwire: ERROR unknown active position, using default animation")
                elwire_animations.connected_animation(
                    run_while=is_connected_and_active_and_charged, initial_animation=False
                )
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
