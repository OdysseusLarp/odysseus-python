import board
import pwmio
import digitalio
import neopixel

# Globals
NEOPIXEL_PIN = board.D12
NEOPIXEL_COUNT = 24
NEOPIXEL_ORDER = neopixel.GRB
# Max brightness of Neopixel library. Brightness is handled internally instead.
NEOPIXEL_BRIGHTNESS = 1
# Default internal initial brightness
NEOPIXEL_INTERNAL_BRIGHTNESS = 20

# EL-wire PWM pin
EL_WIRE_PIN = board.D13

# Pins that indicate where battery is connected. Each can be floating or grounded.
# These are converted to an int as bits, 0 = floating, 1 = GND.
# First pin in array is the least significant bit.
LOCATION_INPUT_PINS = [board.D22, board.D23, board.D24, board.D25]

# Big battery location values. These are physically wired into the sockets. Same as in backend.
LOCATION_NONE = 0
LOCATION_ENGINEERING = 1
LOCATION_MEDBAY = 2
LOCATION_SCIENCE = 3
LOCATION_FIGHTER1 = 4
LOCATION_FIGHTER2 = 5
LOCATION_FIGHTER3 = 6

# Approx time from JumpEnd signal (moving to inactive state) to the coming-out-of-jump climax, seconds
JUMP_EXIT_TIME = 4
