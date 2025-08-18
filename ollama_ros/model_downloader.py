#!/usr/bin/env python3
#coding:utf-8
import rclpy
from rclpy.node import Node
import os
import time
import ollama
import tkinter as Tkinter
from tkinter import ttk
from subprocess import Popen
from ament_index_python.packages import get_package_share_directory
import yaml
import threading

import getpass

class ModelDownloader(Node):
    def __init__(self):
        super().__init__('model_downloader')
        Popen(["xterm", "-font", "r16", "-fg", "floralwhite", "-bg", "darkslateblue", "-e", "ollama", "serve"])
        self.get_logger().info("ModelDownloader")
        time.sleep(1)
        self.tk = Tkinter.Tk()

        with open(get_package_share_directory("ollama_ros") + "/models/model_list.yaml", "r") as file:
            self.can_download_models_info = yaml.safe_load(file)["models"]

        self.download_models_flag = []
        self.reset_models_info()

        self.row_h_normal = 30
        self.row_h_expanded = 45
        self.row_heights = [self.row_h_normal for _ in self.can_download_models_info]
        self.row_widgets = []

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

    # ---- レイアウトのy位置を計算 ----
    def _row_y(self, i):
        return sum(self.row_heights[:i])

    # ---- ウィンドウ高さの更新 ----
    def _update_window_geometry(self):
        min_h = self.row_h_normal * 2
        total_h = sum(self.row_heights)
        geometry_x = 700
        geometry_y = max(min_h, total_h)
        self.tk.geometry(f"{geometry_x}x{geometry_y}+{(self.width - geometry_x) // 2}+{(self.height - geometry_y) // 2}")

    # ---- 全行の再配置 ----
    def _relayout_all(self):
        self._update_window_geometry()
        for i, w in enumerate(self.row_widgets):
            y = self._row_y(i)
            # ラベル
            if w.get('label'):
                w['label'].place_configure(x=460, y=y)
            # download ボタン
            if w.get('btn_download'):
                w['btn_download'].place_configure(x=150, y=y)
            # delete/copy/push
            if w.get('btn_delete'):
                w['btn_delete'].place_configure(x=150, y=y)
            if w.get('btn_copy'):
                w['btn_copy'].place_configure(x=250, y=y)
            if w.get('btn_push'):
                w['btn_push'].place_configure(x=350, y=y)
            # 進捗
            if w.get('pb'):
                w['pb'].place_configure(x=150, y=y+22)
            if w.get('status_label'):
                w['status_label'].place_configure(x=440, y=y+22)

    # ---- GUI 初期構築 ----
    def create_gui(self):
        self._update_window_geometry()

        # 参照配列を初期化
        self.row_widgets = []
        for i, container_info in enumerate(self.can_download_models_info):
            y = self._row_y(i)

            row = {'label': None, 'btn_download': None, 'btn_delete': None, 'btn_copy': None, 'btn_push': None,
                   'pb': None, 'pv': None, 'status': None, 'status_label': None}
            row['label'] = Tkinter.Label(self.tk, text=container_info, font=("", 15))
            row['label'].place(x=460, y=y)

            if self.download_models_flag[i]:
                row['btn_delete'] = Tkinter.Button(self.tk, width=9, text="delete",
                                                   command=lambda i=i: self.button_clicked_callback("delete", i))
                row['btn_delete'].place(x=150, y=y)
                row['btn_copy'] = Tkinter.Button(self.tk, width=9, text="copy",
                                                 command=lambda i=i: self.button_clicked_callback("copy", i))
                row['btn_copy'].place(x=250, y=y)
                row['btn_push'] = Tkinter.Button(self.tk, width=9, text="push",
                                                 command=lambda i=i: self.button_clicked_callback("push", i))
                row['btn_push'].place(x=350, y=y)
            else:
                row['btn_download'] = Tkinter.Button(self.tk, width=34, text="download",
                                                     command=lambda i=i: self.button_clicked_callback("pull", i))
                row['btn_download'].place(x=150, y=y)

            self.row_widgets.append(row)

        # GUI再起動用ボタン
        Tkinter.Button(self.tk, width=6, text="refresh", command=self.refresh_gui).place(x=0, y=0)
        # GUI停止用ボタン
        Tkinter.Button(self.tk, width=6, text="close", command=self.quit_gui).place(x=0, y=30)

        self.tk.title("[Download] ollama models GUI")
        self.tk.mainloop()

    # ---- 行の拡大/縮小（進捗表示用） ----
    def _expand_row(self, i):
        self.row_heights[i] = self.row_h_expanded
        self._relayout_all()

    def _shrink_row(self, i):
        self.row_heights[i] = self.row_h_normal
        self._relayout_all()

    # ---- 進捗ウィジェット ----
    def _ensure_progress_widgets(self, i):
        w = self.row_widgets[i]
        if w.get('pb') is not None:
            return

        self._expand_row(i)
        y = self._row_y(i)

        pv = Tkinter.DoubleVar(value=0.0)
        pb = ttk.Progressbar(self.tk, orient="horizontal", mode="determinate",
                             length=280, maximum=100, variable=pv)
        pb.place(x=150, y=y+22)

        status = Tkinter.StringVar(value="")
        sl = Tkinter.Label(self.tk, textvariable=status, font=("", 9))
        sl.place(x=440, y=y+22)

        w['pv'] = pv
        w['pb'] = pb
        w['status'] = status
        w['status_label'] = sl

    def _hide_progress_widgets(self, i):
        w = self.row_widgets[i]
        def _apply():
            if w.get('pb') is not None:
                try:
                    w['pb'].stop()
                except Exception:
                    pass
                w['pb'].destroy()
                w['pb'] = None
            if w.get('status_label') is not None:
                w['status_label'].destroy()
                w['status_label'] = None
            w['pv'] = None
            w['status'] = None
            self._shrink_row(i)
        self.tk.after(0, _apply)

    # ---- UI 更新ヘルパ ----
    def _set_status(self, i, text):
        def _apply():
            w = self.row_widgets[i]
            if w.get('status') is not None:
                w['status'].set(text)
        self.tk.after(0, _apply)

    def _set_progress(self, i, value):
        def _apply():
            w = self.row_widgets[i]
            if w.get('pv') is not None:
                w['pv'].set(max(0, min(100, value)))
        self.tk.after(0, _apply)

    def _set_bar_mode(self, i, mode):
        def _apply():
            w = self.row_widgets[i]
            if w.get('pb') is not None:
                pb = w['pb']
                pb.config(mode=mode)
                if mode == "indeterminate":
                    pb.start(10)
                else:
                    pb.stop()
        self.tk.after(0, _apply)

    def _set_button_state(self, btn, state):
        def _apply():
            try:
                btn.config(state=state)
            except Exception:
                pass
        self.tk.after(0, _apply)

    # ---- 行のボタンセットを差し替え ----
    def _switch_row_to_owned(self, i):
        w = self.row_widgets[i]
        y = self._row_y(i)
        if w.get('btn_download'):
            try:
                w['btn_download'].destroy()
            except Exception:
                pass
            w['btn_download'] = None

        if not w.get('btn_delete'):
            w['btn_delete'] = Tkinter.Button(self.tk, width=9, text="delete",
                                             command=lambda i=i: self.button_clicked_callback("delete", i))
            w['btn_delete'].place(x=150, y=y)
        if not w.get('btn_copy'):
            w['btn_copy'] = Tkinter.Button(self.tk, width=9, text="copy",
                                           command=lambda i=i: self.button_clicked_callback("copy", i))
            w['btn_copy'].place(x=250, y=y)
        if not w.get('btn_push'):
            w['btn_push'] = Tkinter.Button(self.tk, width=9, text="push",
                                           command=lambda i=i: self.button_clicked_callback("push", i))
            w['btn_push'].place(x=350, y=y)
        self.download_models_flag[i] = True

    def _switch_row_to_not_owned(self, i):
        w = self.row_widgets[i]
        y = self._row_y(i)
        for k in ('btn_delete', 'btn_copy', 'btn_push'):
            if w.get(k):
                try:
                    w[k].destroy()
                except Exception:
                    pass
                w[k] = None
        if not w.get('btn_download'):
            w['btn_download'] = Tkinter.Button(self.tk, width=34, text="download",
                                               command=lambda i=i: self.button_clicked_callback("pull", i))
            w['btn_download'].place(x=150, y=y)
        self.download_models_flag[i] = False

    # ---- ダウンロード実体（別スレッド） ----
    def _download_in_thread(self, i):
        model = str(self.can_download_models_info[i])
        w = self.row_widgets[i]

        self._ensure_progress_widgets(i)
        if w.get('btn_download'):
            self._set_button_state(w['btn_download'], "disabled")
        self._set_status(i, "starting...")
        self._set_bar_mode(i, "indeterminate")

        try:
            for ev in ollama.pull(model, stream=True):
                status = ev.get("status") or ""
                total = ev.get("total")
                completed = ev.get("completed")

                if total and completed is not None and total > 0:
                    pct = int(completed * 100 / total)
                    self._set_bar_mode(i, "determinate")
                    self._set_progress(i, pct)
                    self._set_status(i, f"{status} ({pct}%)")
                else:
                    self._set_status(i, status)
                    self._set_bar_mode(i, "indeterminate")

            self._set_bar_mode(i, "determinate")
            self._set_progress(i, 100)
            self._set_status(i, "done")
            time.sleep(0.4)
            self._hide_progress_widgets(i)
            self._switch_row_to_owned(i)

        except Exception as e:
            self._set_bar_mode(i, "determinate")
            self._set_progress(i, 0)
            self._set_status(i, f"error: {e}")
            time.sleep(1.0)
            self._hide_progress_widgets(i)
            if w.get('btn_download'):
                self._set_button_state(w['btn_download'], "normal")

    # ---- ボタンクリック処理 ----
    def button_clicked_callback(self, mode, id):
        if mode == "delete":
            ollama.delete(str(self.can_download_models_info[id]))
            self._hide_progress_widgets(id)
            self._switch_row_to_not_owned(id)
            return
        elif mode == "copy":
            self.get_logger().info("copy")
            ollama.copy(str(self.can_download_models_info[id]),
                        f"{os.environ.get('USER')}/{self.can_download_models_info[id]}")
            return
        elif mode == "push":
            self.get_logger().info("push")
            ollama.push(str(self.can_download_models_info[id]))
            return
        elif mode == "pull":
            t = threading.Thread(target=self._download_in_thread, args=(id,), daemon=True)
            t.start()
            return

    # ---- GUI 再構築/終了 ----
    def refresh_gui(self):
        self.can_download_models_info = self.can_download_models_info[:]
        self.download_models_flag = []
        self.row_heights = [self.row_h_normal for _ in self.can_download_models_info]
        for w in self.row_widgets:
            for key in ('label','btn_download','btn_delete','btn_copy','btn_push','pb','status_label'):
                if w.get(key):
                    try:
                        w[key].destroy()
                    except Exception:
                        pass
        self.row_widgets = []
        self.reset_models_info()
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
