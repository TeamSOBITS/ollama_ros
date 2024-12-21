# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException
from rclpy.executors import MultiThreadedExecutor
import time
import datetime
import asyncio
import ollama
from subprocess import Popen
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from sobits_interfaces.action import ChatLlmRecognition
import yaml


class ChatAction(Node):
    def __init__(self):
        super().__init__("ollama_action_server")
        Popen(["xterm", "-font", "r16", "-fg", "floralwhite", "-bg", "darkslateblue", "-e", "ollama", "serve"])

        self.bridge_ = CvBridge()

        # Declare parameters
        self.declare_parameter('prompt_file', '')

        # Get parameters
        self.prompt_file_ = self.get_parameter('prompt_file').get_parameter_value().string_value
        self.yaml_folder_path_ = "/".join(self.prompt_file_.split("/")[:-1]) +"/"

        with open(self.prompt_file_, "r") as file:
            self.prompt_ = yaml.safe_load(file)
        self.ollama_client_ = ollama.AsyncClient()
        self.chat_messages_ = {}
        self.build_prompt()
        self.action_server_ = ActionServer(self, ChatLlmRecognition, "/ollama_action",
            execute_callback=self.chat_ollama_callback, callback_group=ReentrantCallbackGroup(),
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
        feedback.end_flag = False
        feedback.wip_result = ""
        starting_time = time.time()

        async for result in await self.ollama_client_.chat(model=goal_handle.request.model_name, messages=self.chat_messages_[goal_handle.request.room_name], stream=True):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                print('\033[31mGoal canceled\033[0m', flush=True)
                return 0, ""

            feedback.wip_result += result['message']['content']
            print(feedback.wip_result, flush=True)

            if result['done']:
                elapsed_time = time.time() - starting_time
                feedback.end_flag = True
                goal_handle.publish_feedback(feedback)
                return elapsed_time, feedback.wip_result

            goal_handle.publish_feedback(feedback)

    async def chat_ollama_callback(self, goal_handle):
        feedback = ChatLlmRecognition.Feedback()
        response = ChatLlmRecognition.Result()
        print("===============================================", flush=True)
        if ((goal_handle.request.room_name in self.chat_messages_.keys()) != True):
            self.chat_messages_[goal_handle.request.room_name] = []
        if (len(goal_handle.request.image) == 0):
            self.chat_messages_[goal_handle.request.room_name] += [{'role': 'user', 'content': goal_handle.request.request}]
        else:
            dt_now = datetime.datetime.now()
            images = []
            for i in range(len(goal_handle.request.image)):
                img = goal_handle.request.image[i]
                image = self.bridge_.imgmsg_to_cv2(img)
                if img.encoding == "rgb8":
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                save_file_name = self.yaml_folder_path_ + "result_" + str(dt_now.year) + "_" + str(dt_now.month) + "_" + str(dt_now.day) + "_" + str(dt_now.hour) + "_" + str(dt_now.minute) + "_" + str(dt_now.second) + "_label" + str(i) + ".png"
                cv2.imwrite(save_file_name, image)
                images += [save_file_name]
            self.chat_messages_[goal_handle.request.room_name] += [{'role': 'user', 'content': goal_handle.request.request, 'images' : images}]

        try:
            t, res = asyncio.run(self.dynamic_chat(goal_handle, feedback))
        except Exception as e:
            print(f"\033[31mError occurred: {e}\033[0m", flush=True)
            response.elapsed_time = 0
            response.result = ""
            goal_handle.abort()  # 例外が発生した場合、明示的にゴールを中止
            return response

        response.elapsed_time = t
        response.result = res
        if goal_handle.request.is_stack:
            self.chat_messages_[goal_handle.request.room_name] += [{'role': 'assistant', 'content': res}]
        else:
            self.chat_messages_[goal_handle.request.room_name] = self.chat_messages_[goal_handle.request.room_name][:-1]
        goal_handle.succeed()
        print("\n===============================================", flush=True)
        return response
    

    def build_prompt(self):
        self.chat_messages_ = {}
        for rn in self.prompt_.keys():
            self.chat_messages_[str(rn)] = []
            for talk in self.prompt_[rn]:
                if ("user" in list(talk.keys())):
                    self.chat_messages_[str(rn)] += [{"role": "user", "content": talk["user"]}]
                    if ("image" in list(talk.keys())):
                        self.chat_messages_[str(rn)][-1]["images"] = []
                        for img in talk["image"]:
                            if (img[0] == "/"):
                                self.chat_messages_[str(rn)][-1]["images"] += [img]
                            else:
                                self.chat_messages_[str(rn)][-1]["images"] += [self.yaml_folder_path_ + img]
                else:
                    self.chat_messages_[str(rn)] += [{"role": "assistant", "content": talk["assistant"]}]

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