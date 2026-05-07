import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import csv
import os


class HandJointPublisher(Node):
    def __init__(self):
        super().__init__('hand_joint_publisher')

        # Publisher & timer
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.05, self.publish_joint_states)  # 20 Hz

        # Joint names (must match URDF)
        self.joint_names = [
            'hand_synergy',
            'thumb_j1',
            'r1_j1',
            'middle_j1',
            'r2_j1',
            'pinky_j1'
        ]

        # Load ONE EMG column (THUMB + INDEX + MIDDLE)
        self.rms_data = self.load_csv_column(
            '~/Desktop/hand/emg_data_3fingers.csv', column_index=12
        )

        self.index = 0
        self.get_logger().info(f'Loaded {len(self.rms_data)} EMG samples')

        # Scaling
        self.rms_max = max(self.rms_data, default=1.0)
        self.gain = 1.8

        # Smoothing
        self.prev_synergy = 0.0
        self.alpha = 0.2

        # FIXED joints (adjust if needed)
        self.fixed_r2 = 0.0
        self.fixed_pinky = 0.0

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
        if not self.rms_data:
            return

        idx = self.index % len(self.rms_data)

        # Normalize & invert (open → close)
        target = 1.0 - (self.rms_data[idx] / self.rms_max) * self.gain
        target = max(0.0, min(target, 1.0))

        # Smooth
        synergy = self.alpha * target + (1 - self.alpha) * self.prev_synergy
        self.prev_synergy = synergy

        # Publish joint states
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [
            synergy,              # hand_synergy
            -1.6 * synergy,       # thumb_j1
            1.8 * synergy,        # r1_j1 (index)
            1.9 * synergy,        # middle_j1
            self.fixed_r2,        # r2_j1 (FIXED)
            self.fixed_pinky      # pinky_j1 (FIXED)
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
