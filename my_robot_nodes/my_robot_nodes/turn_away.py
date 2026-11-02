#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from lab_interfaces.msg import ObstacleInfo
from my_robot_interfaces.msg import RobotStatus
from std_srvs.srv import SetBool
from my_robot_interfaces.srv import SetTurnSpeed

class TurnAway(Node):
    def __init__(self):
        super().__init__('turn_away')
        
        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('turn_speed', 0.5)
        self.declare_parameter('max_turn_speed', 1.5)

        self.is_enabled = False # Start turned off

        self.sub = self.create_subscription(ObstacleInfo, '/obstacle', self.obstacle_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(RobotStatus, '/robot_status', 10)
        
        self.srv_enable = self.create_service(SetBool, '/turn_away_enable', self.enable_callback)
        self.srv_speed = self.create_service(SetTurnSpeed, '/set_turn_speed', self.set_speed_callback)
        
        self.get_logger().info("Turn Away Node Started (Currently OFF)")

    def enable_callback(self, request, response):
        self.is_enabled = request.data
        if not self.is_enabled:
            self.pub.publish(Twist()) # Send one zero velocity
        response.success = True
        response.message = "Enabled" if self.is_enabled else "Disabled"
        self.get_logger().info(f"Node enabled: {self.is_enabled}")
        return response

    def set_speed_callback(self, request, response):
        max_speed = self.get_parameter('max_turn_speed').value
        if request.turn_speed <= 0.0:
            response.success = False
            response.message = "Speed must be greater than 0"
        elif request.turn_speed > max_speed:
            response.success = False
            response.message = f"Speed exceeds max of {max_speed}"
        else:
            self.set_parameters([rclpy.parameter.Parameter('turn_speed', rclpy.Parameter.Type.DOUBLE, request.turn_speed)])
            response.success = True
            response.message = f"Speed set to {request.turn_speed}"
        
        self.get_logger().info(f"Set turn speed request: {response.message}")
        return response

    def obstacle_callback(self, msg):
        status = RobotStatus()
        status.obstacle_distance = msg.distance

        if not self.is_enabled:
            status.state = "stopped"
            self.status_pub.publish(status)
            return

        fwd = self.get_parameter('forward_speed').value
        trn = self.get_parameter('turn_speed').value
        cmd = Twist()

        if not msg.too_close:
            cmd.linear.x = fwd
            cmd.angular.z = 0.0
            status.state = "forward"
        else:
            cmd.linear.x = 0.0
            if msg.angle > 0: 
                cmd.angular.z = -trn
            else:             
                cmd.angular.z = trn
            status.state = "turning"
            
        self.pub.publish(cmd)
        self.status_pub.publish(status)

def main(args=None):
    rclpy.init(args=args)
    node = TurnAway()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
