import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import csv
import os


class HandJointPublisher(Node):
    def __init__(self):
        super().__init__('hand_joint_publisher')

        # ROS publisher and timer
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.05, self.publish_joint_states)  # 20 Hz

        # Joint names must match URDF
        self.joint_names = [
            'hand_synergy',
            'thumb_j1',
            'r1_j1',
            'middle_j1',
            'r2_j1',
            'pinky_j1'
        ]

        # Load EMG RMS data (FOUR FINGERS ONLY)
        self.rms_data_fingers = self.load_csv_column(
            '~/Desktop/hand/emg_data_fingers.csv', column_index=13
        )

        self.index = 0
        self.get_logger().info(
            f'Loaded {len(self.rms_data_fingers)} samples for fingers'
        )

        # Motion scaling
        self.fingers_max = max(self.rms_data_fingers, default=1.0)
        self.gain = 1.8

        # Smoothing
        self.prev_fingers = 0.0
        self.alpha = 0.2

        # FIXED THUMB POSITION (adjust if needed)
        self.fixed_thumb_pos = -0.25  # radians

    def load_csv_column(self, filepath, column_index):
        data = []
        filepath = os.path.expanduser(filepath)

        if not os.path.exists(filepath):
            self.get_logger().warn(f'CSV file not found: {filepath}')
            return data

        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                try:
                    data.append(float(row[column_index]))
                except (IndexError, ValueError):
                    continue
        return data

    def publish_joint_states(self):
        if not self.rms_data_fingers:
            return

        idx = self.index % len(self.rms_data_fingers)

        # Normalize & invert (0 = open, 1 = closed)
        fingers_target = 1.0 - (self.rms_data_fingers[idx] / self.fingers_max) * self.gain
        fingers_target = max(0.0, min(fingers_target, 1.0))

        # Smooth
        fingers_synergy = (
            self.alpha * fingers_target
            + (1 - self.alpha) * self.prev_fingers
        )
        self.prev_fingers = fingers_synergy

        # Publish JointState
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [
            fingers_synergy,            # hand_synergy
            self.fixed_thumb_pos,       # thumb_j1 (FIXED)
            2.4 * fingers_synergy,      # r1_j1
            2.6 * fingers_synergy,      # middle_j1
            -2.6 * fingers_synergy,     # r2_j1
            -2.3 * fingers_synergy      # pinky_j1
        ]

        self.publisher.publish(msg)
        self.index += 1


def main():
    rclpy.init()
    node = HandJointPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
