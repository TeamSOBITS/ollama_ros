import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory("ollama_ros")    
    config_path = os.path.join(pkg_dir, 'prompt', 'ollama_config.yaml')
    
    return LaunchDescription([
        Node(
            package='ollama_ros',
            executable='ollama_action_server',
            name='ollama_action_server',
            output='screen',
            parameters=[
                config_path,
                {
                    'prompt_file': os.path.join(pkg_dir, 'prompt', 'base_prompt.yaml'),
                    'tool_file': os.path.join(pkg_dir, 'prompt', 'ollama_tools.yaml')
                },
            ]
        ),
    ])