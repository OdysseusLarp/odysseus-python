from odysseus import log
from odysseus.taskbox import *
import random
import time

# Usage:  python3 battery.py --id myid

# Pins that indicate where battery is connected.  Each pin works as a trit:
# 0: floating (not connected), 1: low, 2: high
# First pin in array is the most significant trit.
LOCATION_INPUT_PINS = [4, 5, 6]

# How long to wait for pins to settle after setting pullup/down
PUD_WAIT = 0.002

# How often to force update (in seconds)
FORCE_UPDATE_INTERVAL = 30

# How often to run logic (in seconds)
RUN_INTERVAL = 1.0

default_state = {
    "current_capacity": 1000,
    "full_capacity": 1000,
    "rechargeable": True,
    "connected_position": 0,
    "last_write": 0,  # used internally to force update every 10s
}


def logic(state, backend_change):
    # Update connected_position
    state["connected_position"] = read_position()

    # Update display percentage
    update_charge_display(state["current_capacity"] / state["full_capacity"] * 100)

    # Force update every FORCE_UPDATE_INTERVAL seconds
    if state["last_write"] + FORCE_UPDATE_INTERVAL < time.time():
        state["last_write"] = time.time()

    return state


def read_position():
    position_value = 0

    # First, read with pulldown
    pulldown_states = []
    for pin in LOCATION_INPUT_PINS:
        pi.set_pull_up_down(pin, pigpio.PUD_DOWN)
    sleep(PUD_WAIT)
    for pin in LOCATION_INPUT_PINS:
        pulldown_states.append(pi.read(pin))

    # Then, read with pullup
    for pin in LOCATION_INPUT_PINS:
        pi.set_pull_up_down(pin, pigpio.PUD_UP)
    sleep(PUD_WAIT)
    for i, pin in enumerate(LOCATION_INPUT_PINS):
        pullup_state = pi.read(pin)

        # Determine if the pin is floating, low, or high
        if pulldown_states[i] != pullup_state:
            trit_value = 0  # Floating
        else:
            trit_value = 1 if pullup_state == 0 else 2  # Low or High

        # Calculate position value
        position_value = position_value * 3 + trit_value

    return position_value


def update_charge_display(percentage):
    # TODO: Implement
    print("Charge: " + str(percentage) + "%")


pigpio = None
pi = None


def box_init():
    import pigpio as real_pigpio

    global pi
    global pigpio
    pigpio = real_pigpio
    pi = pigpio.pi()

    # Set input pins
    for pin in LOCATION_INPUT_PINS:
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_OFF)


options = {
    "init": box_init,
    "callback": logic,
    "run_interval": RUN_INTERVAL,
    "initial_state": default_state,
    # "write_interval": 2
    # "mock_init":box_init
}

TaskBoxRunner(options).run()
