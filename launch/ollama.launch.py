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
                {'model_name': 'llava-phi3:latest'},
                {'stack_chat': "true"},
            ]
        ),
    ])
