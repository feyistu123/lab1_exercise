#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from my_robot_interfaces.action import Rotate
import math
import time

class RotateServer(Node):
    def __init__(self):
        super().__init__('rotate_server')
        self.declare_parameter('turn_speed', 0.5)
        
        self._action_server = ActionServer(
            self, Rotate, '/rotate',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)
            
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.current_yaw = 0.0
        self.is_rotating = False
        self.last_yaw = 0.0
        self.total_turned = 0.0

    def odom_callback(self, msg):
        # Extract yaw from quaternion
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

        if self.is_rotating:
            diff = self.current_yaw - self.last_yaw
            # Handle the jump from pi to -pi
            if diff > math.pi: diff -= 2 * math.pi
            elif diff < -math.pi: diff += 2 * math.pi
            self.total_turned += diff
        self.last_yaw = self.current_yaw

    def goal_callback(self, goal_request):
        if goal_request.angle == 0.0:
            self.get_logger().info('Rejecting zero goal')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        target_angle = goal_handle.request.angle
        speed = self.get_parameter('turn_speed').value
        
        cmd_speed = speed if target_angle > 0 else -speed
        
        self.total_turned = 0.0
        self.is_rotating = True
        feedback_msg = Rotate.Feedback()
        
        cmd = Twist()
        cmd.angular.z = cmd_speed
        
        expected_time = abs(target_angle) / speed
        timeout = time.time() + (expected_time * 10) + 5.0 
        
        while abs(self.total_turned) < abs(target_angle) - 0.05:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.pub.publish(Twist())
                self.is_rotating = False
                return Rotate.Result(turned=self.total_turned)
                
            # SAFETY CHECK FOR VIRTUALBOX:
            if time.time() > timeout:
                self.get_logger().warn('Timeout reached! The VM odometry is lagging.')
                break
                
            self.pub.publish(cmd)
            feedback_msg.turned = self.total_turned
            goal_handle.publish_feedback(feedback_msg)
            
            # Wait 0.1 seconds between checks
            await self.sleep(0.1) 

        # Stop the robot
        self.pub.publish(Twist())
        await self.sleep(0.5)
        self.is_rotating = False
        
        goal_handle.succeed()
        self.get_logger().info('Goal succeeded!')
        return Rotate.Result(turned=self.total_turned)

    async def sleep(self, seconds):
        start = time.time()
        while time.time() - start < seconds:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = RotateServer()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
