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

EL_WIRE_PIN = board.D13
el_wire = None
