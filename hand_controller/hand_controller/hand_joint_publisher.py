import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from rcl_interfaces.msg import SetParametersResult
import csv
import os


class HandJointPublisher(Node):
    def __init__(self):
        super().__init__('hand_joint_publisher')

        # -----------------------------
        # PARAMETERS
        # -----------------------------
        self.declare_parameter('mode', 'five')  # three | four | five
        self.mode = self.get_parameter('mode').get_parameter_value().string_value
        self.add_on_set_parameters_callback(self.on_param_change)

        self.get_logger().info(f'Operating mode: {self.mode}')
        
        # -----------------------------
        # ROS
        # -----------------------------
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.05, self.publish_joint_states)

        self.joint_names = [
            'hand_synergy',
            'thumb_j1',
            'r1_j1',
            'middle_j1',
            'r2_j1',
            'pinky_j1'
        ]

        # -----------------------------
        # LOAD DATA BASED ON MODE
        # -----------------------------
        if self.mode == 'three':
            self.csv_path = '~/Desktop/hand/emg_data_3fingers.csv'
            self.column_index = 12
        elif self.mode == 'four':
            self.csv_path = '~/Desktop/hand/emg_data_fingers.csv'
            self.column_index = 13
        elif self.mode == 'five':
            self.csv_path = '~/Desktop/hand/emg_data_5fingers.csv'
            self.column_index = 13
        else:
            self.get_logger().error('Invalid mode! Use: three | four | five')
            rclpy.shutdown()
            return

        self.rms_data = self.load_csv_column(self.csv_path, self.column_index)

        self.index = 0
        self.rms_max = max(self.rms_data, default=1.0)

        # -----------------------------
        # TUNING
        # -----------------------------
        self.gain = 1.8
        self.alpha = 0.2
        self.prev_synergy = 0.0

        # Fixed joints
        self.fixed_thumb = -0.25
        self.fixed_r2 = 0.0
        self.fixed_pinky = 0.0

        self.get_logger().info(f'Loaded {len(self.rms_data)} EMG samples')

    def load_csv_column(self, filepath, column_index):
        data = []
        filepath = os.path.expanduser(filepath)

        if not os.path.exists(filepath):
            self.get_logger().error(f'CSV not found: {filepath}')
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
    
    def on_param_change(self, params):
        for param in params:
            if param.name == 'mode':
                self.mode = param.value
                self.get_logger().info(f'Mode changed to: {self.mode}')
        return SetParametersResult(successful=True)

    def publish_joint_states(self):
        if not self.rms_data:
            return

        idx = self.index % len(self.rms_data)

        # Normalize & invert
        target = 1.0 - (self.rms_data[idx] / self.rms_max) * self.gain
        target = max(0.0, min(target, 1.0))

        # Smooth
        synergy = self.alpha * target + (1 - self.alpha) * self.prev_synergy
        self.prev_synergy = synergy

        # -----------------------------
        # MODE LOGIC
        # -----------------------------
        if self.mode == 'three':
            positions = [
                synergy,
                -1.6 * synergy,
                1.8 * synergy,
                1.9 * synergy,
                self.fixed_r2,
                self.fixed_pinky
            ]

        elif self.mode == 'four':
            positions = [
                synergy,
                self.fixed_thumb,
                1.75 * synergy,
                1.8 * synergy,
                -1.8 * synergy,
                -1.6 * synergy
            ]

        elif self.mode == 'five':
            positions = [
                synergy,
                -2.2 * synergy,
                1.6 * synergy,
                1.8 * synergy,
                -1.8 * synergy,
                -1.6 * synergy
            ]

        # -----------------------------
        # PUBLISH
        # -----------------------------
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = positions

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
