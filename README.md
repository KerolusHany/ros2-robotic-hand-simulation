# Robotic Hand Control System

This ROS2 project implements a control system for a prosthetic robotic hand using Electromyography (EMG) signals. The system includes robot description packages, control nodes, and data processing scripts for different hand configurations.

## Demo Video

[![Demo Video](https://img.youtube.com/vi/WgKHGBrR7w0/0.jpg)](https://youtu.be/WgKHGBrR7w0)

## Project Structure

### Packages

#### `assem2_description`
ROS2 package containing the URDF description of the robotic hand assembly.
- **URDF Model**: `assem2.urdf` - Complete kinematic model exported from SolidWorks
- **Meshes**: STL files for visual and collision geometries
- **Launch Files**:
  - `display.launch.py`: Launches RViz visualization with joint state publishers
  - `gazebo.launch`: ROS1 launch file for Gazebo simulation
- **Configuration**: Joint names configuration file

#### `data_description`
Duplicate of `assem2_description` with identical content.

#### `hand_controller`
ROS2 Python package for EMG-based hand control.
- **Main Node**: `hand_joint_publisher.py` - Publishes joint states based on EMG data
- **Features**:
  - Configurable modes: 3-finger, 4-finger, or 5-finger control
  - Real-time EMG data processing
  - Joint position smoothing and scaling
  - ROS2 parameter interface for mode switching

### Scripts (`files_node/`)

Standalone Python scripts for different control modes:

- `move_five_fingers.py`: Controls all five fingers using EMG data
- `move_four_fingers.py`: Controls four fingers with fixed thumb position
- `move_three_fingers.py`: Controls thumb, index, and middle fingers
- `move_with_math.py`: Test script using sinusoidal motion (no EMG data)

### Data Files (`data_files/`)

CSV files containing EMG sensor readings:
- `emg_data_3fingers.csv`: EMG data for 3-finger mode
- `emg_data_4fingers.csv`: EMG data for 4-finger mode
- `emg_data_5fingers.csv`: EMG data for 5-finger mode
- `emg_data_thumb.csv`: EMG data for thumb-specific control

Each CSV contains time-stamped readings from multiple EMG sensors.

## Installation and Setup

### Prerequisites
- ROS2 (tested with ROS2 Humble)
- Python 3.8+
- Gazebo (for simulation)
- RViz2 (for visualization)

### Building the Packages

```bash
# Navigate to your ROS2 workspace
cd /path/to/your/ros2/workspace

# Clone or copy this project to src/
cp -r /path/to/hand/src/* src/

# Build the packages
colcon build

# Source the workspace
source install/setup.bash
```

## Usage

### Visualization in RViz

Launch the robot visualization:
```bash
ros2 launch assem2_description display.launch.py gui:=true
```

### Running the Hand Controller

#### Using the ROS2 Package
```bash
# 5-finger mode (default)
ros2 run hand_controller hand_joint_publisher

# 4-finger mode
ros2 run hand_controller hand_joint_publisher --ros-args -p mode:=four

# 3-finger mode
ros2 run hand_controller hand_joint_publisher --ros-args -p mode:=three
```

#### Using Standalone Scripts
```bash
# Make sure CSV files are in the expected location (~/Desktop/hand/)
python3 src/files_node/move_five_fingers.py
python3 src/files_node/move_four_fingers.py
python3 src/files_node/move_three_fingers.py
python3 src/files_node/move_with_math.py
```

### Simulation in Gazebo

For ROS1 Gazebo simulation (requires ROS1 bridge):
```bash
roslaunch assem2_description gazebo.launch
```

## Control Modes

### 5-Finger Mode
- Controls all fingers: thumb, index, middle, ring, pinky
- Uses synergy-based control where all fingers move together
- EMG data from `emg_data_5fingers.csv`

### 4-Finger Mode
- Controls index, middle, ring, pinky
- Thumb remains in fixed position
- EMG data from `emg_data_4fingers.csv`

### 3-Finger Mode
- Controls thumb, index, middle fingers
- Ring and pinky remain fixed
- EMG data from `emg_data_3fingers.csv`

## EMG Data Processing

The system processes EMG signals through:
1. **Normalization**: EMG values are normalized to [0,1] range
2. **Inversion**: Higher EMG activity corresponds to hand closing
3. **Smoothing**: Exponential moving average for stable control
4. **Scaling**: Configurable gain factors for each joint
5. **Synergy Mapping**: Single EMG signal controls coordinated finger motion

## Joint Configuration

The hand has the following joints (defined in URDF):
- `hand_synergy`: Master synergy joint
- `thumb_j1`: Thumb proximal joint
- `r1_j1`: Index finger proximal joint
- `middle_j1`: Middle finger proximal joint
- `r2_j1`: Ring finger proximal joint
- `pinky_j1`: Pinky finger proximal joint

## Configuration Parameters

### Hand Controller Parameters
- `mode`: Control mode (`three`, `four`, `five`)
- `gain`: EMG scaling factor (default: 1.8)
- `alpha`: Smoothing factor (default: 0.2)

## Data Format

EMG CSV files contain columns for:
- `Time_s`: Timestamp in seconds
- `Sensor*_EMG1`: EMG readings from individual sensors (1-14)

The control scripts use specific columns:
- 3-finger mode: Column 12
- 4/5-finger modes: Column 13

## Testing

Run the test script for sinusoidal motion testing:
```bash
ros2 run hand_controller hand_joint_publisher  # with math mode
```

## Dependencies

- `rclpy`: ROS2 Python client
- `sensor_msgs`: Joint state messages
- `robot_state_publisher`: Robot state publishing
- `joint_state_publisher`: Joint state publishing
- `joint_state_publisher_gui`: GUI for joint control
- `rviz2`: 3D visualization

## Future Improvements

- Real-time EMG sensor integration
- Advanced control algorithms (PID, impedance control)
- Haptic feedback
- Machine learning-based gesture recognition
- Multi-modal control (voice + EMG)

## License

BSD License (see package.xml files)

## Author

Kerolus Hany

