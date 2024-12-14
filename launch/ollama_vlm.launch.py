from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ollama_ros',
            executable='ollama_action_server_vlm',
            name='ollama_action_server_vlm',
            output='screen',
            parameters=[
                {'model_name': 'llava-phi3:latest'},
                {'stack_chat': "true"},
                {'image': "icon.jpg"},
            ]
        ),
    ])
