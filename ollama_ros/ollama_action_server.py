import os
import json
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor, ExternalShutdownException
import time
import datetime
import ollama 
from subprocess import Popen
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from rcl_interfaces.msg import SetParametersResult
from sobits_interfaces.action import ChatLlmRecognition
import yaml

class ChatAction(Node):
    def __init__(self):
        super().__init__("ollama_action_server")
        Popen(["xterm", "-font", "r16", "-fg", "floralwhite", "-bg", "darkslateblue", "-e", "ollama", "serve"])

        self.bridge_ = CvBridge()

        self.declare_parameter('prompt_file', '')
        self.declare_parameter('tool_file', '')
        self.declare_parameter('ollama.num_ctx', 4096)
        self.declare_parameter('ollama.repeat_last_n', 64)
        self.declare_parameter('ollama.repeat_penalty', 1.1)
        self.declare_parameter('ollama.temperature', 0.7)
        self.declare_parameter('ollama.seed', 42)
        self.declare_parameter('ollama.num_predict', 4096)
        self.declare_parameter('ollama.top_k', 40)
        self.declare_parameter('ollama.top_p', 0.9)
        self.declare_parameter('ollama.json_mode', False)
        self.declare_parameter('ollama.tool_choice', 'none')

        self.prompt_file_ = self.get_parameter('prompt_file').value
        self.yaml_folder_path_ = "/".join(self.prompt_file_.split("/")[:-1]) +"/"
        self.tool_file_ = self.get_parameter('tool_file').value
        self.add_on_set_parameters_callback(self.parameter_callback)
        self.tools_definition_ = None
        self.load_tools()

        with open(self.prompt_file_, "r") as file:
            self.prompt_ = yaml.safe_load(file)
            
        self.ollama_client_ = ollama.Client()
        self.chat_messages_ = {}
        self.build_prompt()

        self.action_server_ = ActionServer(
            self, ChatLlmRecognition, "ollama_action",
            execute_callback=self.chat_ollama_callback, 
            callback_group=ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        self.get_logger().info("\033[93mOllama Server is READY.\033[0m")

    def load_tools(self):
        if self.tool_file_ and os.path.exists(self.tool_file_):
            try:
                with open(self.tool_file_, "r") as file:
                    data = yaml.safe_load(file)
                    self.tools_definition_ = data.get('tools')
                    self.get_logger().info(f"Loaded {len(self.tools_definition_)} tools.")
            except Exception as e:
                self.get_logger().error(f"Failed to load tools: {e}")

    def parameter_callback(self, params):
        for param in params:
            self.get_logger().info(f"\033[94m[Param Update] {param.name} -> {param.value}\033[0m")
            if param.name == 'tool_file':
                self.tool_file_ = param.value
                self.load_tools()
        return SetParametersResult(successful=True)

    def goal_callback(self, goal_request): return GoalResponse.ACCEPT
    def cancel_callback(self, goal_handle): return CancelResponse.ACCEPT

    def _format_tool_call_for_api(self, tool_call_string):
        try:
            tool_data = json.loads(tool_call_string.replace("TOOL_CALL:", ""))
            tool_calls = [{"type": "function", "function": {"name": cmd["name"], "arguments": cmd["args"]}} for cmd in tool_data]
            return {"role": "assistant", "content": "", "tool_calls": tool_calls}
        except Exception:
            return {"role": "assistant", "content": tool_call_string}

    def get_ollama_options(self):
        options = {
            'num_ctx': self.get_parameter('ollama.num_ctx').value,
            'repeat_last_n': self.get_parameter('ollama.repeat_last_n').value,
            'repeat_penalty': self.get_parameter('ollama.repeat_penalty').value,
            'temperature': self.get_parameter('ollama.temperature').value,
            'num_predict': self.get_parameter('ollama.num_predict').value,
            'top_k': self.get_parameter('ollama.top_k').value,
            'top_p': self.get_parameter('ollama.top_p').value,
        }
        seed = self.get_parameter('ollama.seed').value
        if seed != -1: options['seed'] = seed
        return options

    def dynamic_chat(self, goal_handle, feedback):
        feedback.end_flag = False
        feedback.wip_result = ""
        starting_time = time.time()
        tool_buffer = {}

        room_name = goal_handle.request.room_name
        t_choice = str(self.get_parameter('ollama.tool_choice').value)
        j_mode = bool(self.get_parameter('ollama.json_mode').value)
        opts = self.get_ollama_options()
        
        self.get_logger().info(f"\033[95m[Inference Config] tool_choice: {t_choice}, json_mode: {j_mode}, temp: {opts['temperature']}\033[0m")

        api_messages = []
        for m in self.chat_messages_[room_name]:
            msg_copy = m.copy()
            if 'files' in msg_copy:
                msg_copy['images'] = msg_copy.pop('files')
            api_messages.append(msg_copy)

        chat_kwargs = {
            'model': goal_handle.request.model_name,
            'messages': api_messages,
            'stream': True,
            'options': opts
        }

        if j_mode:
            chat_kwargs['format'] = 'json'
            chat_kwargs['messages'].insert(0, {"role": "system", "content": "Respond only in valid JSON format."})

        if t_choice == 'none':
            self.get_logger().info("\033[95m[Internal] Tools are DISABLED for this request.\033[0m")
        elif self.tools_definition_:
            chat_kwargs['tools'] = self.tools_definition_
            if t_choice == 'required':
                chat_kwargs['messages'].insert(0, {"role": "system", "content": "You MUST call a tool."})

        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                response_stream = self.ollama_client_.chat(**chat_kwargs)
                for result in response_stream:
                    if goal_handle.is_cancel_requested:
                        goal_handle.canceled()
                        return 0.0, ""

                    if result['message'].get('content'):
                        content = result['message']['content']
                        feedback.wip_result += content
                        print(content, end="", flush=True)
                        goal_handle.publish_feedback(feedback)

                    if result['message'].get('tool_calls'):
                        for tc in result['message']['tool_calls']:
                            idx = tc.get('index', 0)
                            tool_buffer[idx] = tc

                    if result['done']:
                        print("") 
                        elapsed_time = float(time.time() - starting_time)
                        feedback.end_flag = True
                        final_tool_calls = list(tool_buffer.values())
                        
                        if final_tool_calls:
                            simplified_commands = [{"name": tc['function']['name'], "args": tc['function']['arguments']} for tc in final_tool_calls]
                            result_text = f"TOOL_CALL:{json.dumps(simplified_commands)}"
                        else:
                            result_text = feedback.wip_result
                        
                        goal_handle.publish_feedback(feedback)
                        return elapsed_time, result_text

            except ollama.ResponseError as e:
                if e.status_code == 400 and 'tools' in chat_kwargs:
                    self.get_logger().warn(f"Tool error. Retrying without tools...")
                    chat_kwargs.pop('tools')
                    continue
                else: raise e
        return 0.0, feedback.wip_result

    def chat_ollama_callback(self, goal_handle):
        feedback = ChatLlmRecognition.Feedback()
        response = ChatLlmRecognition.Result()
        room_name = goal_handle.request.room_name if goal_handle.request.room_name else 'default'
        
        self.get_logger().info(f"Goal [{room_name}]: {goal_handle.request.request}")
        if room_name not in self.chat_messages_: self.chat_messages_[room_name] = []
            
        if len(goal_handle.request.image) == 0:
            self.chat_messages_[room_name].append({'role': 'user', 'content': goal_handle.request.request})
        else:
            dt_now = datetime.datetime.now()
            images = []
            abs_path = os.path.abspath(self.yaml_folder_path_)
            self.get_logger().info(f"\033[94m[Images] Saving to: {abs_path}\033[0m")
            
            for i in range(len(goal_handle.request.image)):
                img_msg = goal_handle.request.image[i]
                image = self.bridge_.imgmsg_to_cv2(img_msg)

                if img_msg.encoding == 'bgr8':
                    pass
                elif img_msg.encoding == 'bgra8':
                    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
                elif img_msg.encoding == 'rgba8':
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
                elif img_msg.encoding == 'rgb8':
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                else:
                    self.get_logger().error(f"\033[31mUnsupported encoding: {img_msg.encoding}\033[0m")
                    continue

                file_name = (
                    f"result_{dt_now.year}_{dt_now.month:02d}_{dt_now.day:02d}_"
                    f"{dt_now.hour:02d}_{dt_now.minute:02d}_{dt_now.second:02d}_"
                    f"label{i}.png"
                )
                save_path = os.path.join(abs_path, file_name)
                
                cv2.imwrite(save_path, image)
                images.append(save_path)
                self.get_logger().info(f"\033[94m[Images]  -> Saved file: {save_path}\033[0m")
            
            self.chat_messages_[room_name].append({'role': 'user', 'content': goal_handle.request.request, 'files': images})

        try:
            t, res = self.dynamic_chat(goal_handle, feedback)
        except Exception as e:
            self.get_logger().error(f"Execution Error: {e}")
            if goal_handle.is_active:
                goal_handle.abort()
            return response

        if not goal_handle.is_active:
            self.get_logger().warn("Goal is no longer active (likely canceled). Finishing callback.")
            return response

        response.elapsed_time, response.result = t, res
        
        if res.startswith("TOOL_CALL:"):
            self.get_logger().info(f"\033[96m[TOOL CALL] {res.replace('TOOL_CALL:', '')}\033[0m")
        else:
            self.get_logger().info(f"\033[92m[CHAT RESPONSE] {res}\033[0m")

        if goal_handle.request.is_stack:
            content = self._format_tool_call_for_api(res) if res.startswith("TOOL_CALL:") else {'role': 'assistant', 'content': res}
            self.chat_messages_[room_name].append(content)
        else: 
            if self.chat_messages_[room_name]:
                self.chat_messages_[room_name].pop()
            
        goal_handle.succeed()
        return response

    def build_prompt(self):
        if not self.prompt_: return
        for rn, history in self.prompt_.items():
            self.chat_messages_[str(rn)] = []
            for talk in history:
                if "system" in talk: self.chat_messages_[str(rn)].append({"role": "system", "content": talk["system"]})
                elif "user" in talk:
                    msg = {"role": "user", "content": talk["user"]}
                    if "files" in talk: msg["files"] = [img if img.startswith("/") else self.yaml_folder_path_ + img for img in talk["files"]]
                    elif "image" in talk:
                        msg["files"] = [img if img.startswith("/") else self.yaml_folder_path_ + img for img in talk["image"]]
                    self.chat_messages_[str(rn)].append(msg)
                elif "model" in talk:
                    content = talk["model"]
                    self.chat_messages_[str(rn)].append(self._format_tool_call_for_api(content) if content.startswith("TOOL_CALL:") else {"role": "assistant", "content": content})

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor()
    try:
        node = ChatAction()
        executor.add_node(node)
        try:
            executor.spin()
        finally:
            executor.remove_node(node)
            node.destroy_node()
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()