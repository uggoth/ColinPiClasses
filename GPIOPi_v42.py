module_name = 'GPIOPi_v42.py'
module_create_date = '202304280945'

import ColObjects_v13 as ColObjects
import time
import pigpio
gpio = pigpio.pi()

#GPIO class reference:
#   GPIO
#      Reserved
#      DigitalInput
#         Button
#         Control Pin
#         IRSensor
#         Switch
#         USEcho
#         Volts
#      DigitalOutput
#         LED
#         USTrigger
#      PWM
#         Buzzer
#         GPIOServo
#   Compound objects with multiple inheritance
#      FIT0441Motor
#      L298Motor
#      L298NStepper
#      HCSR04

class GPIO(ColObjects.ColObj):

    first_pin_no = 2
    last_pin_no = 27
    free_code = 'FREE'
    allocated = [free_code]*(last_pin_no + 1)
    ids = {}

    def allocate(pin_no, obj):
        if ((pin_no < GPIO.first_pin_no) or (pin_no > GPIO.last_pin_no)):
            raise ColObjects.ColError('pin no {} not in range {} to {}'.format(
                pin_no, GPIO.first_pin_no, GPIO.last_pin_no))
        if GPIO.allocated[pin_no] != GPIO.free_code:
            raise ColObjects.ColError('pin no {} already in use'.format(pin_no))
        GPIO.allocated[pin_no] = obj
        return True

    def deallocate(pin_no):
        GPIO.allocated[pin_no] = GPIO.free_code

    def str_allocated():
        out_string = ''
        for i in range(len(GPIO.allocated)):
            if GPIO.allocated[i] == GPIO.free_code:
                out_string += '{:02} : --FREE--'.format(i) + "\n"
            else:
                obj = GPIO.allocated[i]
                out_string += ('{:02}'.format(i) + ' : ' +
                                '{:18}'.format(obj.name) + "\n")
        return out_string
    
    def get_type_list(type_code):
        type_list = {}
        for obj in GPIO.allocated:
            if obj.type_code == type_code:
                type_list[obj.name] = obj
        return type_list

    valid_type_codes = {'INFRA_RED':'INPUT',
                        'BUTTON':'INPUT',
                        'BUZZER':'OUTPUT',
                        'US_TRIGGER':'OUTPUT',
                        'US_ECHO':'INPUT',
                        'SWITCH':'INPUT',
                        'VOLTS':'INPUT',
                        'ADC':'INPUT',
                        'LED':'OUTPUT',
                        'CONTROL':'INPUT',
                        'INPUT':'INPUT',
                        'OUTPUT':'OUTPUT',
                        'SERVO':'OUTPUT',
                        'MOTOR':'OUTPUT',
                        'NEOPIXEL':'OUTPUT'}
    
    def __init__(self, name, type_code, pin_no):
        super().__init__(name)
        if type_code not in GPIO.valid_type_codes:
            raise ColObjects.ColError (type_code + 'not in' + GPIO.valid_type_codes)
        self.type_code = type_code
        GPIO.allocate(pin_no, self)
        self.pin_no = pin_no
        self.previous = 'UNKNOWN'

    def close(self):
        GPIO.deallocate(self.pin_no)
        super().close()

class Reserved(GPIO):
    def __init__(self, name, type_code, pin_no):
        super().__init__(name, type_code, pin_no)

class DigitalOutput(GPIO):
    def __init__(self, name, type_code, pin_no):
        super().__init__(name, type_code, pin_no)
        gpio.set_mode(pin_no, pigpio.OUTPUT)
    def set(self, new_state):
        if new_state == 'ON':
            gpio.write(self.pin_no, 1)
            return True
        elif new_state == 'OFF':
            gpio.write(self.pin_no, 0)
            return True
        return False

class StepPattern(ColObjects.ColObj):
    def __init__(self, name):
        self.name = name

class StepPatternStandard(StepPattern):
    def __init__(self, tiny_us=5.0, small_us=10.0, large_us=300.0):
        super().__init__('Standard')
        self.tiny_us = tiny_us
        self.small_us = small_us
        self.large_us = large_us
        self.pattern = [
             ['PAUSE', small_us], ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','OFF'], 
             ['PAUSE', small_us], ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','OFF'], 
             ['PAUSE', small_us], ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','OFF'], 
             ['PAUSE', small_us], ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','ON'],  ['PIN4','OFF'], 
             ['PAUSE', small_us], ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','OFF'], 
             ['PAUSE', small_us], ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','ON'],  
             ['PAUSE', small_us], ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON'],  
             ['PAUSE', small_us], ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON'],
             ['PAUSE', small_us]]

class L298NStepper(ColObjects.Motor):
    def __init__(self, name, pin_1_no, pin_2_no, pin_3_no, pin_4_no):
        self.name = name
        self.pin_1 = DigitalOutput(pin_no=pin_1_no, type_code='MOTOR', name=self.name+'_'+str(pin_1_no)) 
        self.pin_2 = DigitalOutput(pin_no=pin_2_no, type_code='MOTOR', name=self.name+'_'+str(pin_2_no)) 
        self.pin_3 = DigitalOutput(pin_no=pin_3_no, type_code='MOTOR', name=self.name+'_'+str(pin_3_no)) 
        self.pin_4 = DigitalOutput(pin_no=pin_4_no, type_code='MOTOR', name=self.name+'_'+str(pin_4_no))
        self.pin_list = {'PIN1':self.pin_1,'PIN2':self.pin_2,'PIN3':self.pin_3,'PIN4':self.pin_4}
        self.pattern_object = StepPatternStandard()
        self.pattern = self.pattern_object.pattern
    def step_on(self, direction, large_pause='DEFAULT'):
        million=1000000.0
        tiny_pause = self.pattern_object.tiny_us/million
        if large_pause=='DEFAULT':
            large_pause = self.pattern_object.large_us/million
        if direction not in ['CLK','ANTI']:
            raise(ColObjects.ColError('direction must be CLK or ANTI'))
        step_count = len(self.pattern)
        for i in range(step_count):
            if direction == 'ANTI':
                this_step = self.pattern[i]
            else:
                this_step = self.pattern[(step_count-1)-i]
            what = this_step[0]
            how = this_step[1]
            if what == 'PAUSE':
                time.sleep(how / million)
            else:
                pin = self.pin_list[what]
                pin.set(how)
                time.sleep(tiny_pause)
        time.sleep(large_pause)
                    

if __name__ == "__main__":
    print (module_name)
    
