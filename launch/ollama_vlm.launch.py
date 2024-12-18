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
                {'model_name': 'llama3.2-vision'},
                {'stack_chat': "true"},
                {'image': "icon.jpg"},
            ]
        ),
    ])
