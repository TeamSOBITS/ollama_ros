#!/usr/bin/env python3
#coding:utf-8
import rclpy
from rclpy.node import Node
import os
import time
import ollama
import tkinter as Tkinter
from subprocess import Popen
from ament_index_python.packages import get_package_share_directory

import getpass

class ModelDownloader(Node):
    def __init__(self):
        super().__init__('model_downloader')
        Popen(["xterm", "-font", "r16", "-fg", "floralwhite", "-bg", "darkslateblue", "-e", "ollama", "serve"])
        self.get_logger().info("ModelDownloader")
        time.sleep(1)
        self.tk = Tkinter.Tk()
        # モデルの一覧
        self.can_download_models_info = ["llama3", "llama3.3", "llama3.2", "llama3.2-vision", "deepseek-r1", "phi3", "phi4", "llava", "minicpm-v", "dbrx", "dolphin-mixtral", "llama2-chinese", "llava-llama3", "llava-phi3"]
        self.download_models_flag = []
        self.reset_models_info()
        self.iconfile = Tkinter.PhotoImage(file=get_package_share_directory("ollama_ros") + "/img/icon.png")
        self.width = self.tk.winfo_screenwidth()
        self.height = self.tk.winfo_screenheight()
        self.tk.call('wm', 'iconphoto', self.tk._w, self.iconfile)

    def reset_models_info(self):
        models = ollama.list()
        if models.get("models"):
            for m in self.can_download_models_info:
                self.download_models_flag.append(False)
                for lm in models["models"]:
                    if m == lm["name"].replace(":latest", ""):
                        self.download_models_flag[-1] = True
                        break
            for lm in models["models"]:
                match_flag = False
                for m in self.can_download_models_info:
                    if m == lm["name"].replace(":latest", ""):
                        match_flag = True
                        break
                if not match_flag:
                    self.can_download_models_info.append(lm["name"].replace(":latest", ""))
                    self.download_models_flag.append(True)
        else:
            for m in self.can_download_models_info:
                self.download_models_flag.append(False)

    def create_gui(self):
        # GUIウィンドウの大きさを定義する
        geometry_x = 700
        if len(self.can_download_models_info) < 2:
            geometry_y = 30 * 2
        else:
            geometry_y = 30 * len(self.can_download_models_info)

        # ウィンドウ位置を中央に配置
        self.tk.geometry(f"{geometry_x}x{geometry_y}+{(self.width - geometry_x) // 2}+{(self.height - geometry_y) // 2}")

        for i, container_info in enumerate(self.can_download_models_info):
            if self.download_models_flag[i]:
                Tkinter.Button(self.tk, width=9, text="delete", command=lambda i=i: self.button_clicked_callback("delete", i)).place(x=150, y=i * 30)
                Tkinter.Button(self.tk, width=9, text="copy", command=lambda i=i: self.button_clicked_callback("copy", i)).place(x=250, y=i * 30)
                Tkinter.Button(self.tk, width=9, text="push", command=lambda i=i: self.button_clicked_callback("push", i)).place(x=350, y=i * 30)
            else:
                Tkinter.Button(self.tk, width=34, text="download", command=lambda i=i: self.button_clicked_callback("pull", i)).place(x=150, y=i * 30)

            Tkinter.Label(text=container_info, font=("", 15)).place(x=460, y=i * 30)

        # GUI再起動用ボタン
        Tkinter.Button(self.tk, width=6, text="refresh", command=self.refresh_gui).place(x=0, y=0)
        # GUI停止用ボタン
        Tkinter.Button(self.tk, width=6, text="close", command=self.quit_gui).place(x=0, y=30)

        self.tk.title("[Download] ollama models GUI")
        self.tk.mainloop()

    def button_clicked_callback(self, mode, id):
        if mode == "delete":
            ollama.delete(str(self.can_download_models_info[id]))
        elif mode == "copy":
            self.get_logger().info("copy")
            ollama.copy(str(self.can_download_models_info[id]), f"{os.environ.get('USER')}/{self.can_download_models_info[id]}")
        elif mode == "pull":
            ollama.pull(str(self.can_download_models_info[id]))
        elif mode == "push":
            self.get_logger().info("push")
            ollama.push(str(self.can_download_models_info[id]))
        self.refresh_gui()

    def refresh_gui(self):
        self.can_download_models_info = []
        self.download_models_flag = []
        self.tk.quit()
        self.tk.destroy()
        self.__init__()
        self.create_gui()

    def quit_gui(self):
        self.tk.quit()
        self.tk.destroy()


def main(args=None):
    rclpy.init(args=args)
    node = ModelDownloader()
    node.create_gui()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
