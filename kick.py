from odysseus.taskbox import TaskBoxRunner
import pigpio

# Box that detects when a contact is opened or closed and fixes the box in that case.
# Kicking a metal plate with a contactor on the other side will fix the box.

CALLS_PER_SECOND = 1.0

default_state = {
    "status": "initial",
    "config": {
        "pin": 14,
    },
}

callback = None
gpio_pin = None
pi = None


def logic(state, backend_change):
    global callback
    global gpio_pin
    if state["config"]["pin"] != gpio_pin:
        gpio_pin = state["config"]["pin"]
        init_pin(gpio_pin)
    if callback.tally() > 0:
        print("Kicked! tally =", callback.tally())
        if state["status"] != "fixed":
            state["status"] = "fixed"
        callback.reset_tally()

    return state


def init_pin(pin):
    print("Initializing pin", pin)
    global pi
    global callback
    if not pi:
        pi = pigpio.pi()
    if callback:
        callback.cancel()

    pi.set_mode(pin, pigpio.INPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_UP)
    callback = pi.callback(pin, pigpio.EITHER_EDGE)


options = {
    "callback": logic,
    "run_interval": 1.0 / CALLS_PER_SECOND,
    "initial_state": default_state,
}
TaskBoxRunner(options).run()
