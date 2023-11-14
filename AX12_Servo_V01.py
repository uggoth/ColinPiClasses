module_name = 'AX12_Servo_V01.py'
module_created_at = '14/Nov/2023'

import ColObjects_Pi_V15 as ColObjects
from pyax12.connection import Connection
import time

class AX12_Servo(ColObjects.Servo):
    def __init__(self, name, connection, dynamixel_id):
        super().__init__(name, 'Dynamixel AX12 Servo')
        self.connection = connection
        self.dynamixel_id = dynamixel_id
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
    if True:
        conn = Connection(port='/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-port0', baudrate=1000000)
        test = AX12_Servo('test', conn, 16)
        time.sleep(0.1)
        test.close()
        conn.close()
    if False:
        conn = Connection(port='/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-port0', baudrate=1000000)
        test = AX12_Servo('test', conn, 16)
        time.sleep(1)
        print (test.min_angle_value, test.max_angle_value)
        print (test.a_factor, test.b_factor)
        print (test.move_to_and_wait(-100))
        print (test.move_to_and_wait(-10))
        print (test.move_to_and_wait(64.3))
        print (test.move_to_and_wait(100))
        print (test.move_to_and_wait(-100))
        test.close()
        conn.close()
