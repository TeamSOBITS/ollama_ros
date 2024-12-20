import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ollama_ros',
            executable='ollama_action_server',
            name='ollama_action_server',
            output='screen',
            parameters=[
                {'prompt_file': os.path.join(get_package_share_directory("ollama_ros"), 'prompt', 'base_prompt.yaml')},
            ]
        ),
    ])
