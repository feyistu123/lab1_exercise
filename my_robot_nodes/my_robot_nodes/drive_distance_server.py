#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from my_robot_interfaces.action import DriveDistance
import math
import time

class DriveDistanceServer(Node):
    def __init__(self):
        super().__init__('drive_distance_server')
        self.declare_parameter('forward_speed', 0.2)
        
        self._action_server = ActionServer(
            self, DriveDistance, '/drive_distance',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)
            
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.is_driving = False

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

    def goal_callback(self, goal_request):
        if goal_request.distance == 0.0:
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing drive goal...')
        target_distance = goal_handle.request.distance
        speed = self.get_parameter('forward_speed').value
        
        cmd_speed = speed if target_distance > 0 else -speed
        
        self.start_x = self.current_x
        self.start_y = self.current_y
        self.is_driving = True
        feedback_msg = DriveDistance.Feedback()
        
        cmd = Twist()
        cmd.linear.x = cmd_speed
        
        # Timeout safety
        expected_time = abs(target_distance) / speed
        timeout = time.time() + (expected_time * 10) + 5.0
        
        while True:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.pub.publish(Twist())
                self.is_driving = False
                return DriveDistance.Result(distance=0.0)
                
            self.pub.publish(cmd)
            
            # Calculate distance traveled
            dx = self.current_x - self.start_x
            dy = self.current_y - self.start_y
            dist_traveled = math.sqrt(dx**2 + dy**2)
            
            feedback_msg.distance = dist_traveled
            goal_handle.publish_feedback(feedback_msg)
            
            if dist_traveled >= abs(target_distance) - 0.05:
                break
                
            if time.time() > timeout:
                self.get_logger().warn('Timeout reached! Odom lag.')
                break
                
            await self.sleep(0.1)

        self.pub.publish(Twist())
        await self.sleep(0.5)
        self.is_driving = False
        
        goal_handle.succeed()
        return DriveDistance.Result(distance=dist_traveled)

    async def sleep(self, seconds):
        start = time.time()
        while time.time() - start < seconds:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = DriveDistanceServer()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
