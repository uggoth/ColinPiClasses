# HOLMES Input Output Facilities

import time
start_time = time.strftime('%Y %m %d %H:%M:%S')
import logging
logging.basicConfig(filename='/home/pi/aaa_ioif.log',level=logging.INFO)
logging.debug('********* ioif starting at ' + start_time)
import math
import os
import maestro_v11 as maestro
import pigpio
gpio = pigpio.pi()
import picamera, picamera.array
import numpy as np

def get_cpu_secs():
    global gpio
    result = float(gpio.get_current_tick()) / 1000000.0
    return result

controllers = {}

controllers['PI_GPIO'] = {}
controllers['PI_GPIO']['INSTANCE'] = gpio
controllers['PI_GPIO']['TYPE'] = 'GPIO'
controllers['PI_GPIO']['PARMS'] = {'INPUT_LOW': 0, 'INPUT_HIGH': 1, 'OUTPUT_LOW': 0, 'OUTPUT_HIGH': 1}
controllers['PI_GPIO']['PINS'] = {18:'D', 23:'D', 24:'D', 25:'D', 12:'D', 16:'D', 20:'D', 21:'D',
                                   4:'D', 17:'D', 27:'D', 22:'D',  5:'D',  6:'D', 13:'D', 19:'D', 26:'D'}

port_types = {}
port_types['IRP'] = {'DESC': 'IR proximity',      'INPUT': True,  'DIGITAL': True,  'PULLUP': 'UP',  'NORMALLY': 'OFF'}
port_types['IRE'] = {'DESC': 'IR edge detect',    'INPUT': True,  'DIGITAL': True,  'PULLUP': 'UP',  'NORMALLY': 'ON'}
port_types['FLD'] = {'DESC': 'Flame Detector',    'INPUT': True,  'DIGITAL': True,  'PULLUP': 'NO',  'NORMALLY': 'ON'}
port_types['SWI'] = {'DESC': 'Mechanical Switch', 'INPUT': True,  'DIGITAL': True,  'PULLUP': 'UP',  'NORMALLY': 'OFF'}
port_types['FIN'] = {'DESC': 'Flag In',           'INPUT': True,  'DIGITAL': True,  'PULLUP': 'UP',  'NORMALLY': 'OFF'}
port_types['ANA'] = {'DESC': 'Analogue Sensor',   'INPUT': True,  'DIGITAL': False, 'PULLUP': 'NO'}
port_types['FOU'] = {'DESC': 'Flag Out',          'INPUT': False, 'DIGITAL': True,                  'NORMALLY': 'OFF'}
port_types['REL'] = {'DESC': 'Relay',             'INPUT': False, 'DIGITAL': True,                  'NORMALLY': 'OFF'}
port_types['LED'] = {'DESC': 'LED',               'INPUT': False, 'DIGITAL': True,                  'NORMALLY': 'OFF'}
port_types['STP'] = {'DESC': 'Stepper Motor',     'INPUT': False, 'DIGITAL': True,                  'NORMALLY': 'OFF'}
port_types['SRV'] = {'DESC': 'Servo',             'INPUT': False, 'DIGITAL': False}

port_map = {}
port_map['SEGMENT_1_LEFT_PIN1']       = {'NAME': 'LEFT Motor Pin 1',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 4}
port_map['SEGMENT_1_LEFT_PIN2']       = {'NAME': 'LEFT Motor Pin 2',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 17}
port_map['SEGMENT_1_LEFT_PIN3']       = {'NAME': 'LEFT Motor Pin 3',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 27}
port_map['SEGMENT_1_LEFT_PIN4']       = {'NAME': 'LEFT Motor Pin 4',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 22}

port_map['SEGMENT_1_RIGHT_PIN1']       = {'NAME': 'RIGHT Motor Pin 1',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 12}
port_map['SEGMENT_1_RIGHT_PIN2']       = {'NAME': 'RIGHT Motor Pin 2',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 16}
port_map['SEGMENT_1_RIGHT_PIN3']       = {'NAME': 'RIGHT Motor Pin 3',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 20}
port_map['SEGMENT_1_RIGHT_PIN4']       = {'NAME': 'RIGHT Motor Pin 4',   'TYPE': 'STP', 'CONTROLLER': 'PI_GPIO',  'PORT': 21}

port_map['RED_LED']     = {'NAME': 'Red LED',       'TYPE': 'LED', 'CONTROLLER': 'PI_GPIO', 'PORT': 8}
port_map['GREEN_LED']   = {'NAME': 'Green LED',     'TYPE': 'LED', 'CONTROLLER': 'PI_GPIO', 'PORT': 13}
port_map['RED_BUTTON']  = {'NAME': 'Red Button',    'TYPE': 'SWI', 'CONTROLLER': 'PI_GPIO', 'INVERT':True, 'PORT': 7}
port_map['GREEN_BUTTON']= {'NAME': 'Green Button',  'TYPE': 'SWI', 'CONTROLLER': 'PI_GPIO', 'INVERT':True, 'PORT': 19}
port_map['DIP_1']       = {'NAME': 'DIP Switch 1',  'TYPE': 'SWI', 'CONTROLLER': 'PI_GPIO', 'INVERT':True, 'PORT': 25}
port_map['DIP_2']       = {'NAME': 'DIP Switch 2',  'TYPE': 'SWI', 'CONTROLLER': 'PI_GPIO', 'INVERT':True, 'PORT': 26}
port_map['DIP_3']       = {'NAME': 'DIP Switch 3',  'TYPE': 'SWI', 'CONTROLLER': 'PI_GPIO', 'INVERT':True, 'PORT': 6}

previous = {}

motor_list = {}

motor_list['SEGMENT_1'] = {}
motor_list['SEGMENT_1']['ANTICLOCKWISE_DISTANCE_FACTOR'] = 1.0
motor_list['SEGMENT_1']['CLOCKWISE_DISTANCE_FACTOR'] = 1.0
motor_list['SEGMENT_1']['STEP_PATTERN'] = 'STANDARD'
motor_list['SEGMENT_1']['MOTORS'] = ['LEFT','RIGHT'] # ['RIGHT'] # ['LEFT'] # 

motor_list['SEGMENT_1']['LEFT'] = {}
motor_list['SEGMENT_1']['LEFT']['DISTANCE'] = 0
motor_list['SEGMENT_1']['LEFT']['FINAL_SPEED'] = 0
motor_list['SEGMENT_1']['LEFT']['SMOOTHNESS'] = 0
motor_list['SEGMENT_1']['LEFT']['ITERATIONS'] = 0
motor_list['SEGMENT_1']['LEFT']['PINS'] = {}
motor_list['SEGMENT_1']['LEFT']['PINS']['PIN1'] = 'SEGMENT_1_LEFT_PIN1'
motor_list['SEGMENT_1']['LEFT']['PINS']['PIN2'] = 'SEGMENT_1_LEFT_PIN2'
motor_list['SEGMENT_1']['LEFT']['PINS']['PIN3'] = 'SEGMENT_1_LEFT_PIN3'
motor_list['SEGMENT_1']['LEFT']['PINS']['PIN4'] = 'SEGMENT_1_LEFT_PIN4'

motor_list['SEGMENT_1']['RIGHT'] = {}
motor_list['SEGMENT_1']['RIGHT']['DISTANCE'] = 0
motor_list['SEGMENT_1']['RIGHT']['FINAL_SPEED'] = 0
motor_list['SEGMENT_1']['RIGHT']['SMOOTHNESS'] = 0
motor_list['SEGMENT_1']['RIGHT']['ITERATIONS'] = 0
motor_list['SEGMENT_1']['RIGHT']['PINS'] = {}
motor_list['SEGMENT_1']['RIGHT']['PINS']['PIN1'] = 'SEGMENT_1_RIGHT_PIN1'
motor_list['SEGMENT_1']['RIGHT']['PINS']['PIN2'] = 'SEGMENT_1_RIGHT_PIN2'
motor_list['SEGMENT_1']['RIGHT']['PINS']['PIN3'] = 'SEGMENT_1_RIGHT_PIN3'
motor_list['SEGMENT_1']['RIGHT']['PINS']['PIN4'] = 'SEGMENT_1_RIGHT_PIN4'

arm_speed_factor = 0.025
maximum_speed = 10
minimum_speed = 0.001
maximum_smoothness = 15
minimum_smoothness = 0
spin_factor = 1.4

step_patterns = {}

pause = 0.01   # varies from installation to installation
step_patterns['RIO_RAND'] = [
             ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','ON'],  ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','ON'],  ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','ON'],  ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON'],  ['PAUSE', pause],
             ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON'],  ['PAUSE', pause]
             ]

pause = 0.01   # varies from installation to installation
step_patterns['RIO_RAND_2'] = [
             ['PIN1','ON'],  ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','ON'],  ['PIN2','ON'],  ['PIN3','ON'],  ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','ON'],  ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','ON'],  ['PIN4','ON'],  ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','ON'],  ['PAUSE', pause],
             ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','ON'],  ['PAUSE', pause],
             ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON'],  ['PAUSE', pause],
             ['PIN1','ON'],  ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','ON'],  ['PAUSE', pause]
             ]

pause = 0.01   # varies from installation to installation
step_patterns['RIO_RAND_3'] = [
             ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','OFF'], ['PAUSE', pause],
             ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON'],  ['PAUSE', pause]
             ]

pause = 0.01   # varies from installation to installation
step_patterns['STANDARD'] = [
             ['PAUSE', pause], ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','OFF'], 
             ['PAUSE', pause], ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','OFF'], 
             ['PAUSE', pause], ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','ON'],  ['PIN4','OFF'], 
             ['PAUSE', pause], ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','ON'],  ['PIN4','OFF'], 
             ['PAUSE', pause], ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','OFF'], 
             ['PAUSE', pause], ['PIN1','OFF'], ['PIN2','ON'],  ['PIN3','OFF'], ['PIN4','ON'],  
             ['PAUSE', pause], ['PIN1','OFF'], ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON'],  
             ['PAUSE', pause], ['PIN1','ON'],  ['PIN2','OFF'], ['PIN3','OFF'], ['PIN4','ON']
             ]

def initialise_input_port(interface):
    global port_map, port_types, controllers
    port_config = port_map[interface]
    port_type = port_config['TYPE']
    port_type_config = port_types[port_type]
    is_input = port_type_config['INPUT']
    controller_name = port_config['CONTROLLER']
    controller_config = controllers[controller_name]
    controller_type = controller_config['TYPE']
    if is_input and controller_type == 'GPIO':
        controller_instance = controllers[controller_name]['INSTANCE']
        port = port_config['PORT']
        controller_instance.set_mode(port, pigpio.INPUT)
        if port_type_config['PULLUP'] == 'UP':
            controller_instance.set_pull_up_down(port, pigpio.PUD_UP)
        elif port_type_config['PULLUP'] == 'DOWN':
            controller_instance.set_pull_up_down(port, pigpio.PUD_DOWN)
        else:
            controller_instance.set_pull_up_down(port, pigpio.PUD_OFF)

def set_speed(interface, new_speed):
    global port_map, controllers
    controller_name = port_map[interface]['CONTROLLER']
    controller_type = controllers[controller_name]['TYPE']
    if (controller_type == 'MAESTRO'):
        port = port_map[interface]['PORT']
        controller_instance = controllers[controller_name]['INSTANCE']
        controller_instance.setSpeed(port, new_speed)
        return True
    else:
        return False

def set_acceleration(interface, new_acceleration):
    global port_map, controllers
    controller_name = port_map[interface]['CONTROLLER']
    controller_type = controllers[controller_name]['TYPE']
    if (controller_type == 'MAESTRO'):
        port = port_map[interface]['PORT']
        controller_instance = controllers[controller_name]['INSTANCE']
        controller_instance.setAccel(port, new_acceleration)
        return True
    else:
        return False

def get_moving_state(interface):
    global port_map, controllers
    controller_name = port_map[interface]['CONTROLLER']
    controller_type = controllers[controller_name]['TYPE']
    if (controller_type == 'MAESTRO'):
        port = port_map[interface]['PORT']
        controller_instance = controllers[controller_name]['INSTANCE']
        return controller_instance.getMovingState()
    else:
        return False

def wait_for_it():
    while get_moving_state('LEFT_ELBO'):
        time.sleep(0.01)

def set_positions(position_list):
    global previous
    for joint in position_list:
        new_position = position_list[joint]
        set_value(joint,position_list[joint])
        previous[joint] = new_position
    wait_for_it()

def adjust_positions(adjustment_list):
    global previous
    rotated = 0
    for joint in adjustment_list:
        delta = adjustment_list[joint]
        new_position = previous[joint] + delta
        set_value(joint, new_position)
        previous[joint] = new_position
        if joint == 'ROTATE':
            rotated = delta
    if rotated > 0:
        extra_pause = float(abs(rotated)) / 500.0
        time.sleep(extra_pause)
    wait_for_it()

def initialise_output_port(interface):
    global port_map, port_types, controllers
    port_config = port_map[interface]
    port_type = port_config['TYPE']
    if port_type == 'REL':   # Initialised in hardware
        return True
    port_type_config = port_types[port_type]
    is_input = port_type_config['INPUT']
    controller_name = port_config['CONTROLLER']
    controller_config = controllers[controller_name]
    controller_type = controller_config['TYPE']
    if controller_type == 'GPIO':
        controller_instance = controllers[controller_name]['INSTANCE']
        port = port_map[interface]['PORT']
        controller_instance.set_mode(port, pigpio.OUTPUT)
        controller_instance.write(port,0)
    if 'SPEED' in port_config:
        sub_result = set_speed(interface, port_config['SPEED'])
    if 'ACCELERATION' in port_config:
        sub_result = set_acceleration(interface, port_config['ACCELERATION'])
    if 'NORMALLY' in port_type_config:
        sub_result = set_state(interface, port_type_config['NORMALLY'])
    return True

def initialise_all_ports():
    global port_map, port_type
    for interface in port_map:
        port_config = port_map[interface]
        this_type = port_config['TYPE']
        type_config = port_types[this_type]
        if type_config['INPUT']:
            initialise_input_port(interface)
        else:
            initialise_output_port(interface)
    return True

def set_value(interface, state):
    global port_map, port_types, controllers
    port_config = port_map[interface]
    port_type = port_config['TYPE']
    port_type_config = port_types[port_type]
    is_input = port_type_config['INPUT']
    if not is_input:
        controller_name = port_config['CONTROLLER']
        controller_config = controllers[controller_name]
        controller_type = controller_config['TYPE']
        if controller_type == 'GPIO':
            controller_instance = controllers[controller_name]['INSTANCE']
            port = port_map[interface]['PORT']
            controller_instance.write(port,state)
        elif controller_type == 'MAESTRO':
            controller_instance = controllers[controller_name]['INSTANCE']
            port = port_map[interface]['PORT']
            controller_instance.setTarget(port, state)

def get_value(interface):
    global port_map, port_type, controllers
    logging.debug('get_value: called for '  + interface)
    result = {}
    result['SUCCESS'] = False
    port_config = port_map[interface]
    port_type = port_config['TYPE']
    port_type_config = port_types[port_type]
    is_input = port_type_config['INPUT']
    if is_input:
        controller_name = port_config['CONTROLLER']
        controller_config = controllers[controller_name]
        controller_type = controller_config['TYPE']
        port = port_config['PORT']
        if controller_type == 'MAESTRO':
            controller_instance = controllers[controller_name]['INSTANCE']
            position = controller_instance.getPosition(port)
            logging.debug('get_value: Returning ' + str(position) + ' for ' + interface)
            result['SUCCESS'] = True
            result['VALUE'] = position
            return result
        elif controller_type == 'GPIO':
            controller_instance = controllers[controller_name]['INSTANCE']
            position = controller_instance.read(port)
            logging.debug('get_value: Returning ' + str(position) + ' for ' + interface)
            result['SUCCESS'] = True
            result['VALUE'] = position
            return result
        else:
            result['SUCCESS'] = False
            return result
    else:
        result['SUCCESS'] = False
        return result

def get_servo_position(interface):
    global port_map, port_type, controllers
    logging.debug('get_value: called for '  + interface)
    result = {}
    result['SUCCESS'] = False
    port_config = port_map[interface]
    port_type = port_config['TYPE']
    if port_type == 'SRV':
        controller_name = port_config['CONTROLLER']
        controller_config = controllers[controller_name]
        controller_type = controller_config['TYPE']
        port = port_config['PORT']
        if controller_type == 'MAESTRO':
            controller_instance = controllers[controller_name]['INSTANCE']
            position = controller_instance.getPosition(port)
            logging.debug('get_value: Returning ' + str(position) + ' for ' + interface)
            result['SUCCESS'] = True
            result['VALUE'] = position
            return result
        else:
            result['SUCCESS'] = False
            return result
    else:
        result['SUCCESS'] = False
        return result

def get_state(interface):
    global port_map, controllers
    result = {}
    result['SUCCESS'] = False
    result['STATE'] = 'UNKNOWN'
    sub_result = get_value(interface)
    if sub_result['SUCCESS']:
        port_config = port_map[interface]
        controller_name = port_config['CONTROLLER']
        controller_config = controllers[controller_name]
        low = controller_config['PARMS']['INPUT_LOW']
        high = controller_config['PARMS']['INPUT_HIGH']
        position = sub_result['VALUE']
        if position <= low:
            if 'INVERT' in port_config:
                result['STATE'] = 'ON'
            else:
                result['STATE'] = 'OFF'
            result['SUCCESS'] = True
            return result
        elif position >= high:
            if 'INVERT' in port_config:
                result['STATE'] = 'OFF'
            else:
                result['STATE'] = 'ON'
            result['SUCCESS'] = True
            return result
        else:
            result['SUCCESS'] = False
            return result
    else:
        result['SUCCESS'] = False
        return result

def wait_for(flasher, button, seconds):
    result = {}
    result['SUCCESS'] = False
    check_interval = 0.01
    loops = int(float(seconds) / check_interval)
    on_time = 0.1
    off_time = 0.1
    flash_time = on_time + off_time
    led_state = 'OFF'
    set_state(flasher, led_state)
    for i in range(loops):
        time.sleep(check_interval)
        sub_result = get_state(button)
        if sub_result['SUCCESS']:
            state = sub_result['STATE']
        else:
            return result
        duration = float(i) * check_interval
        if state == 'ON':
            result['SUCCESS'] = True
            result['DURATION'] = duration
            return result
        phase = duration % flash_time
        if phase > on_time:
            required_state = 'OFF'
        else:
            required_state = 'ON'
        if led_state != required_state:
            set_state(flasher, required_state)
            led_state = required_state
    return result

def set_state(interface, state):
    global port_map, controllers
    result = {}
    result['SUCCESS'] = False
    port_config = port_map[interface]
    if 'INVERT' in port_config:
        if state == 'ON':
            this_state = 'OFF'
        else:
            this_state = 'ON'
    else:
        this_state = state
    controller_name = port_config['CONTROLLER']
    controller_config = controllers[controller_name]
    if this_state == 'ON':
        high = controller_config['PARMS']['OUTPUT_HIGH']
        set_value(interface, high)
        result['SUCCESS'] = True
    elif this_state == 'OFF':
        low = controller_config['PARMS']['OUTPUT_LOW']
        set_value(interface, low)
        result['SUCCESS'] = True
    return result

def gpio_flash_on(controller_instance, pin):
    controller_instance.set_PWM_frequency(pin,10)
    controller_instance.set_PWM_dutycycle(pin,20)

def gpio_flash_off(controller_instance, pin):
    controller_instance.set_PWM_dutycycle(pin,0)

def led_flash(interface,state):
    if interface in port_map:
        port_config = port_map[interface]
        if port_config['TYPE'] == 'LED':
            controller_name = port_config['CONTROLLER']
            controller_config = controllers[controller_name]
            controller_type = controller_config['TYPE']
            if controller_type == 'GPIO':
                pin = port_map[interface]['PORT']
                controller_instance = controller_config['INSTANCE']
                if state == 'ON':
                    gpio_flash_on(controller_instance, pin)
                else:
                    gpio_flash_off(controller_instance, pin)
                return True
            elif controller_type == 'MAESTRO':
                logging.warning('Interface ' + interface + ' not flash capable')
                return False
            else:
                logging.warning('Interface ' + interface + ' not flash capable')
                return False
    
    return False

def step_on(drive_train, which_iteration):
    global step_patterns, motor_list, maximum_speed, minimum_speed, maximum_smoothness
    which_pattern = motor_list[drive_train]['STEP_PATTERN']
    step_pattern = step_patterns[which_pattern]
    step_count = len(step_pattern)
    done_summat = False
    hold_time = 0.0
    quarter_hold_time = 0.0

    for i in range(0,step_count):
        for this_motor in motor_list[drive_train]['MOTORS']:

            speed = motor_list[drive_train][this_motor]['SPEED']
            if speed > maximum_speed:
                speed = maximum_speed
            if speed < minimum_speed:
                speed = minimum_speed

            smoothness = motor_list[drive_train][this_motor]['SMOOTHNESS']
            if smoothness > maximum_smoothness:
                smoothness = maximum_smoothness
            if smoothness < 0:
                smoothness = 0

            iterations = motor_list[drive_train][this_motor]['ITERATIONS']
            if which_iteration <= iterations:
                direction = motor_list[drive_train][this_motor]['DIRECTION']
                if direction == 'ANTICLOCKWISE':
                    this_step = step_pattern[i]
                elif direction == 'CLOCKWISE':
                    this_step = step_pattern[step_count - i - 1]
                what = this_step[0]
                how = this_step[1]
                if what == 'PAUSE':
                    if speed < maximum_speed:
                        hold_time = (float(how) * (maximum_speed / speed)) / 1000.0
                    else:
                        hold_time = float(how) / 1000.0

                    if smoothness > 0:
                        half_way = iterations / 2
                        if which_iteration < half_way:
                            if which_iteration < smoothness:
                                hold_time = hold_time + ((smoothness - which_iteration) / 1000.0)
                        elif ((iterations - which_iteration) < smoothness):
                            hold_time = hold_time + ((smoothness - (iterations - which_iteration)) / 1000.0)
                    quarter_hold_time = hold_time / 4.0
                    
                if what != 'PAUSE':
                    port_name = motor_list[drive_train][this_motor]['PINS'][what]
                    set_state(port_name, how)
                    time.sleep(quarter_hold_time)

                done_summat = True
    if done_summat:
        return True
    else:
        return False

def drive(drive_train):
    global motor_list
    # distance is in millimetres for fore and aft, or degrees for turns
    result = {}
    result['SUCCESS'] = False
    max_iterations = 0
    for motor in motor_list[drive_train]['MOTORS']:
        distance = motor_list[drive_train][motor]['DISTANCE']
        #print (distance)
        direction = motor_list[drive_train][motor]['DIRECTION']
        factor = motor_list[drive_train][direction + '_DISTANCE_FACTOR']
        iterations = int(distance * factor)
        logging.debug('drive iterations ' + str(iterations))
        motor_list[drive_train][motor]['ITERATIONS'] = iterations
        if iterations > max_iterations:
            max_iterations = iterations
    for i in range(max_iterations):
        if not step_on(drive_train, i):
            result['SUCCESS'] = False
            return result
    result['ITERATIONS'] = i
    result['SUCCESS'] = True
    return result

def check_sensors(required_list, finished_list):
    global port_map, port_type
    result = {}
    result['SUCCESS'] = True
    result['INPUT'] = 'NONE'
    for sensor in required_list:
        required_state = required_list[sensor]
        sub_result = get_state(sensor)
        state = sub_result['STATE']
        if state != required_state:
            logging.debug(sensor + ' required ' + required_state + ' but is ' + state)
            result['SUCCESS'] = False
            result['INPUT'] = sensor
            result['STATE'] = state
            return result
    for sensor in finished_list:
        finished_state = finished_list[sensor]
        sub_result = get_state(sensor)
        state = sub_result['STATE']
        if state == finished_state:
            logging.debug('finished ' + sensor + ' ' + state)
            result['SUCCESS'] = True
            result['INPUT'] = sensor
            result['STATE'] = state
            return result
    result['SUCCESS'] = True
    result['INPUT'] = 'NONE'
    return result

def drive_until(drive_train, required_list, finished_list):
    global motor_list
    #print (drive_train)
    # distance is in millimetres for fore and aft, or degrees for turns
    result = {}
    result['SUCCESS'] = False
    result['ITERATIONS'] = 0
    result['INPUT'] = 'NONE'
    max_iterations = 0
    for motor in motor_list[drive_train]['MOTORS']:
        #print (motor)
        distance = motor_list[drive_train][motor]['DISTANCE']
        #print (distance)
        direction = motor_list[drive_train][motor]['DIRECTION']
        which_factor = direction + '_DISTANCE_FACTOR'
        #print (which_factor)
        factor = motor_list[drive_train][which_factor]
        iterations = int(distance * factor)
        motor_list[drive_train][motor]['ITERATIONS'] = iterations
        if iterations > max_iterations:
            max_iterations = iterations
    for i in range(max_iterations):
        result['ITERATIONS'] = i
        if not step_on(drive_train,i):
            result['SUCCESS'] = False
            return result
        sub_result = check_sensors(required_list, finished_list)
        if not sub_result['SUCCESS']:
            result['SUCCESS'] = False
            result['INPUT'] = sub_result['INPUT']
            result['STATE'] = sub_result['STATE']
            return result
        if sub_result['INPUT'] != 'NONE':
            result['SUCCESS'] = True
            result['INPUT'] = sub_result['INPUT']
            result['STATE'] = sub_result['STATE']
            return result
    result['SUCCESS'] = True
    return result

def fwd(millimetres, speed=10, smoothness=0):
    global motor_list
    motor_list['SEGMENT_1']['LEFT']['DIRECTION'] = 'CLOCKWISE'
    motor_list['SEGMENT_1']['LEFT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['LEFT']['SPEED'] = speed
    motor_list['SEGMENT_1']['LEFT']['SMOOTHNESS'] = smoothness
    motor_list['SEGMENT_1']['RIGHT']['DIRECTION'] = 'ANTICLOCKWISE'
    motor_list['SEGMENT_1']['RIGHT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['RIGHT']['SPEED'] = speed
    motor_list['SEGMENT_1']['RIGHT']['SMOOTHNESS'] = smoothness
    return drive('SEGMENT_1')
    
def rev(millimetres, speed=10, smoothness=0):
    global motor_list
    motor_list['SEGMENT_1']['LEFT']['DIRECTION'] = 'ANTICLOCKWISE'
    motor_list['SEGMENT_1']['LEFT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['LEFT']['SPEED'] = speed
    motor_list['SEGMENT_1']['LEFT']['SMOOTHNESS'] = smoothness
    motor_list['SEGMENT_1']['RIGHT']['DIRECTION'] = 'CLOCKWISE'
    motor_list['SEGMENT_1']['RIGHT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['RIGHT']['SPEED'] = speed
    motor_list['SEGMENT_1']['RIGHT']['SMOOTHNESS'] = smoothness
    return drive('SEGMENT_1')

def spin_left(millimetres, speed=10, smoothness=0):
    global motor_list
    motor_list['SEGMENT_1']['LEFT']['DIRECTION'] = 'ANTICLOCKWISE'
    motor_list['SEGMENT_1']['LEFT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['LEFT']['SPEED'] = speed
    motor_list['SEGMENT_1']['LEFT']['SMOOTHNESS'] = smoothness
    motor_list['SEGMENT_1']['RIGHT']['DIRECTION'] = 'ANTICLOCKWISE'
    motor_list['SEGMENT_1']['RIGHT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['RIGHT']['SPEED'] = speed
    motor_list['SEGMENT_1']['RIGHT']['SMOOTHNESS'] = smoothness
    return drive('SEGMENT_1')

def spin_right(millimetres, speed=10, smoothness=0):
    global motor_list
    motor_list['SEGMENT_1']['LEFT']['DIRECTION'] = 'CLOCKWISE'
    motor_list['SEGMENT_1']['LEFT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['LEFT']['SPEED'] = speed
    motor_list['SEGMENT_1']['LEFT']['SMOOTHNESS'] = smoothness
    motor_list['SEGMENT_1']['RIGHT']['DIRECTION'] = 'CLOCKWISE'
    motor_list['SEGMENT_1']['RIGHT']['DISTANCE'] = millimetres
    motor_list['SEGMENT_1']['RIGHT']['SPEED'] = speed
    motor_list['SEGMENT_1']['RIGHT']['SMOOTHNESS'] = smoothness
    return drive('SEGMENT_1')

def float_all_steppers():
    global motor_list
    for drive_train in motor_list:
        #print drive_train
        for motor in motor_list[drive_train]['MOTORS']:
            #print motor
            for pin in motor_list[drive_train][motor]['PINS']:
                #print pin
                set_state(motor_list[drive_train][motor]['PINS'][pin], 'OFF')
    return True

def float_drive_train(drive_train):
    for motor in motor_list[drive_train]['MOTORS']:
        for pin in motor_list[drive_train][motor]['PINS']:
            set_state(motor_list[drive_train][motor]['PINS'][pin], 'OFF')
    return True

def stop_all_controllers():
    for controller_name in controllers:
        controller_config = controllers[controller_name]
        controller_type = controller_config['TYPE']
        controller_instance = controllers[controller_name]['INSTANCE']
        if controller_type == 'GPIO':
            controller_instance.stop()
        elif controller_type == 'MAESTRO':
            controller_instance.close()

NULL_DISCRIMINATION_FACTOR = 1.5
RED_DISCRIMINATION_FACTOR = 2

def print_colour_result(result):
    global NULL_DISCRIMINATION_FACTOR
    global RED_DISCRIMINATION_FACTOR
    print ('Colour: ' + result['COLOUR'])
    print ('Red: Null: ' + str(result['NULL_RED']) + ', Counter: ' + str(result['COUNTER_RED']))
    print ('Green: Null: ' + str(result['NULL_GREEN']) + ', Counter: ' + str(result['COUNTER_GREEN']))
    print ('Blue: Null: ' + str(result['NULL_BLUE']) + ', Counter: ' + str(result['COUNTER_BLUE']))
    print ('Total: Null: ' + str(result['NULL_TOTAL']) + ', Counter: ' + str(result['COUNTER_TOTAL']))
    print ('Null Discriminator: ' + str(result['NULL_DISCRIMINATOR']) +
           ', (null_total * ' + str(NULL_DISCRIMINATION_FACTOR) +
           ') Actual ratio: {0:.2f}'.format(float(result['COUNTER_TOTAL']) / float(result['NULL_TOTAL'])))
    print ('Red Discriminator: ' + str(result['RED_DISCRIMINATOR']) +
           ', (null_green * ' + str(RED_DISCRIMINATION_FACTOR) +
           ') Actual ratio: {0:.2f}'.format(float(result['COUNTER_GREEN']) / float(result['NULL_GREEN'])))
    print (' ')


def detect_colour():
    global NULL_DISCRIMINATION_FACTOR
    global RED_DISCRIMINATION_FACTOR
    result = {}
    result['SUCCESS'] = False
    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(2)
        with picamera.array.PiRGBArray(camera) as output:
            camera.capture(output,'rgb')
            v_dim = 200
            h_dim = 300
            pixels = v_dim * h_dim
            v_start = 900
            v_end = v_start + v_dim
            h_start = 650
            h_end = h_start + h_dim
            counter_sums = np.sum(np.sum(output.array[v_start:v_end,h_start:h_end],axis=0),axis=0)
            counter_red = counter_sums[0] / pixels
            counter_green = counter_sums[1] / pixels
            counter_blue = counter_sums[2] / pixels
            counter_total = counter_red + counter_green + counter_blue
            v_start = 100
            v_end = v_start + v_dim
            h_start = 650
            h_end = h_start + h_dim
            null_sums = np.sum(np.sum(output.array[v_start:v_end,h_start:h_end],axis=0),axis=0)
            null_red = null_sums[0] / pixels
            null_green = null_sums[1] / pixels
            null_blue = null_sums[2] / pixels
            null_total = null_red + null_green + null_blue
    result['SUCCESS'] = True
    result['COUNTER_TOTAL'] = counter_total
    result['COUNTER_RED'] = counter_red
    result['COUNTER_GREEN'] = counter_green
    result['COUNTER_BLUE'] = counter_blue
    result['NULL_TOTAL'] = null_total
    result['NULL_RED'] = null_red
    result['NULL_GREEN'] = null_green
    result['NULL_BLUE'] = null_blue
    null_discriminator = int(null_total * NULL_DISCRIMINATION_FACTOR)
    result['NULL_DISCRIMINATOR'] = null_discriminator
    red_discriminator = int(null_green * RED_DISCRIMINATION_FACTOR)
    result['RED_DISCRIMINATOR'] = red_discriminator
    if (counter_total < null_discriminator):
        result['COLOUR'] = 'NULL'
    elif (counter_green > red_discriminator):
        result['COLOUR'] = 'YELLOW'
    else:
        result['COLOUR'] = 'RED'
    return result
