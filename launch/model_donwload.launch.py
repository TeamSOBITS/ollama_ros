import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ollama_ros',
            executable='model_downloader',
            name='model_downloader',
            output='screen'
        ),
    ])
