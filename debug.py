from odysseus import log
from odysseus.taskbox import TaskBoxRunner
from datetime import datetime

# Usage:  python3 debug.py --url https://server --user username --passwd password --id debugbox --verbose

# Debugging box that prints out status


default_state = {
    "debug": 1,
    "config": {},
}


def logic(state, backend_change):
    current_date_time = datetime.now()
    if backend_change:
        print(current_date_time.strftime("%Y-%m-%d %H:%M:%S") + f" BACKEND CHANGE: state={state}")
    else:
        print(current_date_time.strftime("%Y-%m-%d %H:%M:%S") + f" state={state}")
    return state


options = {
    "callback": logic,
    "run_interval": 1.0,
    "initial_state": default_state,
}
TaskBoxRunner(options).run()
