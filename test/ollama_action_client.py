#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import actionlib
from ollama_python.msg import ChatOllamaAction
from ollama_python.msg import ChatOllamaGoal
from ollama_python.msg import ChatOllamaActionFeedback


feedback_msg = ChatOllamaActionFeedback()
def actionfeedback_callback(msg):
    global feedback_msg
    feedback_msg = msg


def ollama_client():
    global feedback_msg
    action_client = actionlib.SimpleActionClient("/ollama_action", ChatOllamaAction)
    rospy.Subscriber("/ollama_action/feedback", ChatOllamaActionFeedback, actionfeedback_callback)
    action_client.wait_for_server()

    goal = ChatOllamaGoal()
    goal.room_name = input("room_name >>> ")
    goal.request = input("request >>> ")
    goal.is_service = False     # 途中経過状態のメッセージを送って欲しければFalse．返答のみで十分ならTrueで良い

    action_client.send_goal(goal)

    wip_result = ""
    while not feedback_msg.feedback.end_flag:
        if ((len(wip_result) != len(feedback_msg.feedback.wip_result))):
            wip_result = feedback_msg.feedback.wip_result
            print("\n------------------FEEDBACK--------------------")     # こちらはFeedbackとして黄色で出力されます．おそらく未完成の文が順に出力されているでしょう
            print("\033[33m", wip_result, "\033[0m")
            print("----------------------------------------------")

    action_client.wait_for_result()
    result = action_client.get_result()

    print("\n------------------RESULT--------------------")     # こちらは最終的な出力が緑色で出力されます．
    print("Result: \033[92m",result.result)
    print("\t\t\t\t\t\033[0m(Elapsed Time: ", result.elapsed_time, ")")  # 返答までにかかった時間も出力されます
    print("--------------------------------------------")


if __name__ ==  '__main__':
    try:
        rospy.init_node('ollama_action_client')
        ollama_client()
    except rospy.ROSInterruptException:
        pass