#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interfaces.action import Rotate
# We import DriveDistance from the lab's package
from my_robot_interfaces.action import DriveDistance
import math

class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver')
        self.declare_parameter('side_length', 0.5)
        
        self.rotate_client = ActionClient(self, Rotate, '/rotate')
        self.drive_client = ActionClient(self, DriveDistance, '/drive_distance')

    def send_drive_goal(self, distance):
        self.drive_client.wait_for_server()
        goal = DriveDistance.Goal()
        goal.distance = distance
        self.get_logger().info(f'Sending drive goal: {distance}m')
        future = self.drive_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            return False
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return True

    def send_rotate_goal(self, angle):
        self.rotate_client.wait_for_server()
        goal = Rotate.Goal()
        goal.angle = angle
        self.get_logger().info(f'Sending rotate goal: {angle} rad')
        future = self.rotate_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            return False
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return True

    def run_square(self):
        side_length = self.get_parameter('side_length').value
        turn_angle = math.pi / 2.0 # 90 degrees in radians
        
        for i in range(4):
            self.get_logger().info(f'--- Side {i+1} ---')
            if not self.send_drive_goal(side_length):
                self.get_logger().error(f'Drive failed on side {i+1}')
                return
            if not self.send_rotate_goal(turn_angle):
                self.get_logger().error(f'Rotate failed on side {i+1}')
                return
                
        self.get_logger().info('Square complete!')

def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()
    node.run_square()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
