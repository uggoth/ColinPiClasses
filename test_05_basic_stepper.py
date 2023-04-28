module_name = 'test_05_basic_stepper.py'
module_create_date = '202304271448'

print (module_name, 'starting')

import ColObjects_v13 as ColObj
import GPIOPi_v42 as GPIO
gpio = GPIO.gpio
test_stepper = GPIO.L298NStepper('Test Stepper', 6, 13, 19, 26)
start = gpio.get_current_tick()
million = 1000000.0
large_us = 3000
large_pause = float(large_us) / million
seconds = 5
while True:
    test_stepper.step_on('CLK', large_pause)
    this = gpio.get_current_tick()
    diff_s = GPIO.pigpio.tickDiff(start, this) / million
    if diff_s > seconds:
        break
end = gpio.get_current_tick()
diff = GPIO.pigpio.tickDiff(start, end)
print (large_us, diff)
test_stepper.close()

print (module_name, 'finishing')
