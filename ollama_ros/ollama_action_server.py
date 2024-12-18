#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException
from rclpy.executors import MultiThreadedExecutor
import time
import asyncio
import ollama
from subprocess import Popen
from sobits_interfaces.action import ChatLlmRecognition
import yaml


class ChatAction(Node):
    def __init__(self):
        super().__init__("ollama_action_server")
        Popen(["xterm", "-font", "r16", "-fg", "floralwhite", "-bg", "darkslateblue", "-e", "ollama", "serve"])

        # Declare parameters
        self.declare_parameter('model_name', 'llama3')
        self.declare_parameter('stack_chat', 'true')

        # Get parameters
        self.model_name_ = self.get_parameter('model_name').get_parameter_value().string_value
        self.stack_chat_ = self.get_parameter('stack_chat').get_parameter_value().bool_value
        with open("/home/sobits/colcon_ws/src/ollama_python/prompt/base_prompt.yaml", "r") as file:
        # with open("/home/sobits/colcon_ws/src/ollama_ros/prompt/base_prompt.yaml", "r") as file:
            self.prompt_ = yaml.safe_load(file)
        self.ollama_client_ = ollama.AsyncClient()
        self.chat_messages_ = {}
        self.build_prompt()
        self.action_server_ = ActionServer(
            self,
            ChatLlmRecognition,
            "ollama_action",
            execute_callback=self.chat_ollama_callback,
            callback_group=ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)
        self.get_logger().info('Ollama Server is ready and waiting for service requests.')   

    def goal_callback(self, goal_request):
        """Accept or reject a client request to begin an action."""
        # This server allows multiple goals in parallel
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject a client request to cancel an action."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def dynamic_chat(self, goal_handle, feedback):
        starting_time = time.time()

        message = {'role': 'assistant', 'content': ''}
        model = goal_handle.request.room_name
        service_flag = goal_handle.request.is_service
        feedback.end_flag = False
        async for result in await self.ollama_client_.chat(model=self.model_name_, messages=self.chat_messages_[model], stream=True):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return None
            if result['done']:
                self.chat_messages_[model].append(message)
                elapsed_time = time.time() - starting_time
                feedback.end_flag = True
                goal_handle.publish_feedback(feedback)
                return elapsed_time, message['content']

            content = result['message']['content']
            message['content'] += content
            if (service_flag != True):
                print(content)
                feedback.wip_result = message['content']
                goal_handle.publish_feedback(feedback)

    async def chat_ollama_callback(self, goal_handle):
        feedback = ChatLlmRecognition.Feedback()
        response = ChatLlmRecognition.Result()
        print("===============================================")
        if ((goal_handle.request.room_name in self.chat_messages_.keys()) != True):
            self.chat_messages_[goal_handle.request.room_name] = []
        self.chat_messages_[goal_handle.request.room_name].append({'role': 'user', 'content': goal_handle.request.request})

        try:
            t, res = asyncio.run(self.dynamic_chat(goal_handle, feedback))
        except Exception as e:
            self.get_logger().error(f"Error occurred: {e}")
            goal_handle.abort()  # 例外が発生した場合、明示的にゴールを中止
            response.result = "None"
            return response
        response.elapsed_time = t
        response.result = res
        if goal_handle.request.is_service:
            print(res)
        if (self.stack_chat_ != True):
            self.chat_messages_[goal_handle.request.room_name] = self.chat_messages_[goal_handle.request.room_name][:-2]
        goal_handle.succeed()
        print("\n===============================================")
        return response
    

    def build_prompt(self):
        self.chat_messages_ = {}
        for rn in self.prompt_.keys():
            self.chat_messages_[str(rn)] = []
            for argument in self.prompt_[rn]:
                self.chat_messages_[str(rn)] += [{"role": str(list(argument)[0]), "content": argument[str(list(argument)[0])]}]

# メイン
def main(args=None):
    try:
        rclpy.init(args=args)

        chat_action = ChatAction()

        executor = MultiThreadedExecutor()

        rclpy.spin(chat_action, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass

if __name__ == '__main__':
    main()


    