from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Khởi chạy Node IMU
        Node(
            package='my_robot_driver',
            executable='imu_node',
            name='imu_node'
        ),
        # # Khởi chạy Node Siêu âm
        # Node(
        #     package='my_robot_driver',
        #     executable='ultrasonic_node',
        #     name='ultrasonic_node'
        # ),
        # # Thêm Static TF cho IMU ở đây luôn cho tiện
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'imu_link']
        ),
    ])