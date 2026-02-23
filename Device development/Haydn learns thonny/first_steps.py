from picozero import pico_led
import time

# puts the led into a default off state
pico_led.off()

# sets how many times the led will blink
blinks = 6
blinks = blinks*2
i = 0
while i < blinks:
    if i % 2 == 0:
        pico_led.on()
        time.sleep(0.5)
    else:
        pico_led.off()
        time.sleep(0.5)
        i += 1
    