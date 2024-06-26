module_name = 'GPIO_Pi_v48.py'
module_created_at = '20240326'

from importlib.machinery import SourceFileLoader
data_module = SourceFileLoader('Colin', '/home/pi/ColinThisPi/ColinData.py').load_module()
data_object = data_module.ColinData()
data_values = data_object.params
col_objects_version = data_values['ColObjects']
col_objects_name = '/home/pi/ColinPiClasses/' + col_objects_version + '.py'
print (col_objects_name)
ColObjects = SourceFileLoader('ColObjects',col_objects_name).load_module()
import time
def sleep_us(microseconds):
    time.sleep(float(microseconds)/1000000.0)
import pigpio
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
    def __init__(self, name, gpio, type_code, pin_no):
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

class Trigger(DigitalOutput):
    def __init__(self, name, gpio, pin_no):
        super().__init__(name, gpio, 'US_TRIGGER', pin_no)

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
    def __init__(self, name, gpio, pin_1_no, pin_2_no, pin_3_no, pin_4_no):
        super().__init__(name)
        self.pin_1 = DigitalOutput(self.name+'_'+str(pin_1_no), gpio, 'MOTOR', pin_1_no)
        self.pin_2 = DigitalOutput(self.name+'_'+str(pin_2_no), gpio, 'MOTOR', pin_2_no)
        self.pin_3 = DigitalOutput(self.name+'_'+str(pin_3_no), gpio, 'MOTOR', pin_3_no) 
        self.pin_4 = DigitalOutput(self.name+'_'+str(pin_4_no), gpio, 'MOTOR', pin_4_no)
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
    def __init__(self, name, gpio, pin_1_no, pin_2_no, pin_3_no, pin_4_no):
        self.name = name
        self.pin_1 = DigitalOutput(self.name+'_'+str(pin_1_no), gpio, 'MOTOR', pin_1_no)
        self.pin_2 = DigitalOutput(self.name+'_'+str(pin_2_no), gpio, 'MOTOR', pin_2_no)
        self.pin_3 = DigitalOutput(self.name+'_'+str(pin_3_no), gpio, 'MOTOR', pin_3_no) 
        self.pin_4 = DigitalOutput(self.name+'_'+str(pin_4_no), gpio, 'MOTOR', pin_4_no)
        self.pin_list = {'PIN1':self.pin_1,'PIN2':self.pin_2,'PIN3':self.pin_3,'PIN4':self.pin_4}
        self.pins = [self.pin_1,self.pin_2,self.pin_3,self.pin_4]
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
    def float(self):
        for pin in self.pins:
            pin.set('OFF')
    def close(self):
        self.float()
        super().close()

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

class Ranger:
   """
   This class encapsulates a type of acoustic ranger.  In particular
   the type of ranger with separate trigger and echo pins.

   A pulse on the trigger initiates the sonar ping and shortly
   afterwards a sonar pulse is transmitted and the echo pin
   goes high.  The echo pins stays high until a sonar echo is
   received (or the response times-out).  The time between
   the high and low edges indicates the sonar round trip time.
   """

   def __init__(self, pi, trigger, echo):
      """
      The class is instantiated with the Pi to use and the
      gpios connected to the trigger and echo pins.
      """
      self.pi    = pi
      self._trig = trigger
      self._echo = echo

      self._ping = False
      self._high = None
      self._time = None

      self._triggered = False

      self._trig_mode = pi.get_mode(self._trig)
      self._echo_mode = pi.get_mode(self._echo)

      pi.set_mode(self._trig, pigpio.OUTPUT)
      pi.set_mode(self._echo, pigpio.INPUT)

      self._cb = pi.callback(self._trig, pigpio.EITHER_EDGE, self._cbf)
      self._cb = pi.callback(self._echo, pigpio.EITHER_EDGE, self._cbf)

      self._inited = True

   def _cbf(self, gpio, level, tick):
      if gpio == self._trig:
         if level == 0: # trigger sent
            self._triggered = True
            self._high = None
      else:
         if self._triggered:
            if level == 1:
               self._high = tick
            else:
               if self._high is not None:
                  self._time = tick - self._high
                  self._high = None
                  self._ping = True

   def read(self):
      """
      Triggers a reading.  The returned reading is the number
      of microseconds for the sonar round-trip.

      round trip cms = round trip time / 1000000.0 * 34030
      """
      max_duration = 0.1
      if self._inited:
         self._ping = False
         self.pi.gpio_trigger(self._trig)
         start = time.time()
         while not self._ping:
            duration = time.time()-start
            if duration > max_duration:
               #print '*** duration = ' + str(duration) + ' > ' + str(max_duration)
               return 22000
            time.sleep(0.001)
         return self._time
      else:
         return None

   def read_mms(self):
       sub_result = self.read()
       if sub_result is None:
           return None
       return int((sub_result / 200000.0) * 34030.0)

   def cancel(self):
      """
      Cancels the ranger and returns the gpios to their
      original mode.
      """
      if self._inited:
         self._inited = False
         self._cb.cancel()
         self.pi.set_mode(self._trig, self._trig_mode)
         self.pi.set_mode(self._echo, self._echo_mode)


class HCSR04(ColObjects.ColObj):
    def __init__(self, name, gpio, trigger_pin_no, echo_pin_no):
        super().__init__(name)
        self.trigger_pin_no = trigger_pin_no
        GPIO.allocate(trigger_pin_no, self)
        self.echo_pin_no = echo_pin_no
        GPIO.allocate(echo_pin_no, self)
        self.instance = Ranger(gpio, self.trigger_pin_no, self.echo_pin_no)
    def close(self):
        self.instance.cancel()
        GPIO.deallocate(self.trigger_pin_no)
        GPIO.deallocate(self.echo_pin_no)
        super().close()

if __name__ == "__main__":
    print (module_name,'was created at',module_created_at)
    
