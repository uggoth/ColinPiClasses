module_name = 'AX12_Servo_V01.py'
module_created_at = '14/Nov/2023'

from importlib.machinery import SourceFileLoader
colin_data = SourceFileLoader('Colin', '/home/pi/ColinThisPi/ColinData.py').load_module()
my_data = colin_data.ColinData()
version = my_data.params['ColObjects']
ColObjects = SourceFileLoader('Colin', '/home/pi/ColinPiClasses/' + version + '.py').load_module()

from pyax12.connection import Connection
import time

class AX12_Servo(ColObjects.Servo):
    def __init__(self, name, connection, dynamixel_id):
        super().__init__(name, 'Dynamixel AX12 Servo')
        self.connection = connection
        self.dynamixel_id = dynamixel_id
        #print (self.dynamixel_id)
        self.min_angle_value = connection.get_cw_angle_limit(self.dynamixel_id) # set in firmware
        self.max_angle_value = connection.get_ccw_angle_limit(self.dynamixel_id)
        self.a_factor = (self.min_angle_value + self.max_angle_value) / 2.0
        self.b_factor = (self.max_angle_value - self.min_angle_value) / 200.0
        self.clockwise_label = 'CLOCK'
        self.anticlockwise_label = 'ANTI'
    def convert_from_dynamixel(self, in_pos):
        pos = int(in_pos)
        object_pos = int((pos - self.a_factor) / self.b_factor)
        return object_pos
    def convert_to_dynamixel(self, in_pos):
        pos = int(in_pos)
        dynamixel_pos = int(self.a_factor + (self.b_factor * pos))
        return dynamixel_pos
    def move_to(self, pos, speed=50):
        super().move_to(pos, speed)
        dynamixel_pos = self.convert_to_dynamixel(pos)
        self.connection.goto(self.dynamixel_id, dynamixel_pos, speed=speed)
        return dynamixel_pos
    def move_to_and_wait(self, pos, speed=50):
        dynamixel_pos = self.move_to(pos, speed)
        for i in range(1000):
            if not self.connection.is_moving(self.dynamixel_id):
                break
        return dynamixel_pos
    def get_position(self):
        dynamixel_pos = self.connection.get_present_position(self.dynamixel_id)
        object_pos = self.convert_from_dynamixel(dynamixel_pos)
        return object_pos
    def close(self):
        super().close()

if __name__ == "__main__":
    print (module_name,'was created at',module_created_at)
    ax12_list = my_data.params['AX12_LIST']
    if len(ax12_list) > 0:
        ax12_path = my_data.params['AX12_PATH']
        ax12_speed = my_data.params['AX12_SPEED']
        ax12_connection = Connection(port=ax12_path, baudrate=ax12_speed)
        test = AX12_Servo('test', ax12_connection, ax12_list[0])
        time.sleep(0.1)
        test.close()
        ax12_connection.close()
    else:
        print ('no AX12s')
