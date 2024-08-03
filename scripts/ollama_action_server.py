#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import time
import asyncio
import ollama
import actionlib
from ollama_python.msg import ChatOllamaAction        
from ollama_python.msg import ChatOllamaResult
from ollama_python.msg import ChatOllamaFeedback
from subprocess import Popen


class ChatAction:
    def __init__(self):
        Popen(["xterm", "-font", "r16", "-fg", "floralwhite", "-bg", "darkslateblue", "-e", "ollama", "serve"])
        self.model_ = rospy.get_param("/ollama_action_server/model_name", "llama3")
        self.stack_chat_ = rospy.get_param("/ollama_action_server/stack_chat", True)
        self.ollama_client_ = ollama.AsyncClient()
        self.chat_messages_ = {}
        self.build_prompt()
        self.end_flag_ = False
        self.action_server_ = actionlib.SimpleActionServer("/ollama_action", ChatOllamaAction, execute_cb=self.chat_ollama_callback, auto_start=False)
        self.action_server_.start()
    
    async def dynamic_chat(self, mode_name, service_flag_):
        starting_time = time.time()

        message = {'role': 'assistant', 'content': ''}
        async for response in await self.ollama_client_.chat(model=self.model_, messages=self.chat_messages_[mode_name], stream=True):
            if response['done']:
                self.chat_messages_[mode_name].append(message)
                elapsed_time = time.time() - starting_time
                self.end_flag_ = True
                return elapsed_time, message['content']

            content = response['message']['content']
            message['content'] += content
            if not service_flag_:
                print(content, end='', flush=True)
                feedback = ChatOllamaFeedback(wip_result=message['content'], end_flag=False)
                self.action_server_.publish_feedback(feedback)

    def chat_ollama_callback(self, goal):
        print("===============================================")
        if ((goal.room_name in self.chat_messages_.keys()) != True):
            self.chat_messages_[goal.room_name] = []
        self.chat_messages_[goal.room_name].append({'role': 'user', 'content': goal.request})
        t, res = asyncio.run(self.dynamic_chat(goal.room_name, goal.is_service))
        feedback = ChatOllamaFeedback(wip_result=res, end_flag=True)
        self.action_server_.publish_feedback(feedback)
        result = ChatOllamaResult(result=res, elapsed_time=t)
        if goal.is_service:
            print(res)
        if (self.stack_chat_ != True):
            self.chat_messages_[goal.room_name] = self.chat_messages_[goal.room_name][:-2]
        self.action_server_.set_succeeded(result)
        self.end_flag_ = False
        print("\n===============================================")
    

    def build_prompt(self):
        self.chat_messages_ = {}
        prompt = rospy.get_param("ollama_action_server/prompt", {})
        for rn in prompt.keys():
            self.chat_messages_[str(rn)] = []
            for argument in prompt[rn]:
                self.chat_messages_[str(rn)] += [{"role": str(list(argument)[0]), "content": argument[str(list(argument)[0])]}]


if __name__ == '__main__':
    rospy.init_node('ollama_action_server')
    chat_action = ChatAction()
    rospy.spin()