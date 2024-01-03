module_name = 'GPIO_Pi_v46.py'
module_created_at = '202305091139'

from importlib.machinery import SourceFileLoader
ColObjects = SourceFileLoader('ColObjects','/home/pi/ColinPiClasses/ColObjects_Pi_V15.py').load_module()
import time
def sleep_us(microseconds):
    time.sleep(float(microseconds)/1000000.0)
import gpiozero

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
        self.instance = gpiozero.OutputDevice(pin_no)
    def set(self, new_state):
        if new_state == 'ON':
            self.instance.on()
            return True
        elif new_state == 'OFF':
            self.instance.off()
            return True
        return False

class StepPattern(ColObjects.ColObj):
    def __init__(self, name):
        super().__init__(name)

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

class StepPatternShort(ColObjects.ColObj):
    def __init__(self):
        super().__init__('Short Step Pattern')
        self.pattern = [['PIN1','ON'],['PIN4','OFF'],['PIN3','ON'],['PIN1','OFF'],['PIN2','ON'],['PIN3','OFF'],['PIN4','ON'],['PIN2','OFF']]

class L298NStepperShort(ColObjects.Motor):
    def __init__(self, name, pin_1_no, pin_2_no, pin_3_no, pin_4_no):
        super().__init__(name)
        self.pin_1 = DigitalOutput(pin_no=pin_1_no, type_code='MOTOR', name=self.name+'_'+str(pin_1_no)) 
        self.pin_2 = DigitalOutput(pin_no=pin_2_no, type_code='MOTOR', name=self.name+'_'+str(pin_2_no)) 
        self.pin_3 = DigitalOutput(pin_no=pin_3_no, type_code='MOTOR', name=self.name+'_'+str(pin_3_no)) 
        self.pin_4 = DigitalOutput(pin_no=pin_4_no, type_code='MOTOR', name=self.name+'_'+str(pin_4_no))
        self.pin_list = {'PIN1':self.pin_1,'PIN2':self.pin_2,'PIN3':self.pin_3,'PIN4':self.pin_4}
        self.pins = [self.pin_1,self.pin_2,self.pin_3,self.pin_4]
        self.pattern_object = StepPatternShort()
        self.pattern = self.pattern_object.pattern
        self.step_count = len(self.pattern)
    def step_on(self, direction, pause_microseconds=100):
        for i in range(self.step_count):
            if direction == 'ANTI':
                this_step = self.pattern[i]
            else:
                this_step = self.pattern[(self.step_count-1)-i]
            what = this_step[0]
            how = this_step[1]
            pin = self.pin_list[what]
            pin.set(how)
            sleep_us(pause_microseconds)
    def float(self):
        for pin in self.pins:
            pin.set('OFF')
    def close(self):
        self.float()
        super().close()
        

class L298NStepperStandard(ColObjects.Motor):
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

class L298NDCMotor(ColObjects.Motor):
    def __init__(self, name, fwd_pin_no, rev_pin_no):
        self.instance = gpiozero.Motor(fwd_pin_no, rev_pin_no)
    def clk(self, speed=100):
        self.instance.forward(speed/100.0)
    def anti(self, speed=100):
        self.instance.backward(speed/100.0)
    def stop(self):
        self.instance.stop()
    def close(self):
        self.instance.close()
        super().close()

class Switch(ColObjects.Switch):
    def __init__(self, name, pin_no):
        super().__init__(name)
        self.pin_no = pin_no
        self.instance = gpiozero.Button(pin_no, pull_up=True)
    def get(self):
        return self.instance.value
    def wait_for(self, seconds=100):
        return self.instance.wait_for_press(seconds)
    def close(self):
        self.instance.close()
        super().close()

if __name__ == "__main__":
    print (module_name,'was created at',module_created_at)
    
