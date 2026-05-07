import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math


class HandJointPublisher(Node):
    def __init__(self):
        super().__init__('hand_joint_publisher')

        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.05, self.publish_joint_states)

        self.t = 0.0

        # Joint names MUST match URDF
        self.joint_names = [
            'hand_synergy',
            'thumb_j1',
            'r1_j1',
            'middle_j1',
            'r2_j1',
            'pinky_j1'
        ]

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names

        # Test open/close motion
        synergy = 0.5 * (1.0 + math.sin(self.t))

        msg.position = [
            synergy,
            -0.8 * synergy,
            1.2 * synergy,
            1.3 * synergy,
            -1.3 * synergy,
            -1.15 * synergy
        ]

        self.publisher.publish(msg)
        self.t += 0.05


def main():
    rclpy.init()
    node = HandJointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
