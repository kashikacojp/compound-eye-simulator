import tkinter as tk
from   tkinter import ttk
from   tkinter import filedialog
import argparse
import tomllib
import glob
import numpy as np
import cv2
import sys
import os
import tomllib
import tomli_w
import time
from PIL import Image, ImageTk
from update_view_process import update_view_process

class UIViewer:
    def __init__(self, master):
        parser = argparse.ArgumentParser(description='360 Viewer for compound eye simulator')
        prompt = "TOML settings file (e.g., 'settings/*.toml'): "
        default = './settings/settings.toml'
        parser.add_argument('-f','--file', type=str, default=default, help=f"{prompt} (default: {default}): ")
        args = parser.parse_args()
        with open(args.file,mode='rb') as file:
            if not file:
                print(f"Error: Could not open file {args.file}")
                exit()
            self.settings = tomllib.load(file)
        # デフォルト値の設定
        if not 'image_format' in self.settings:
            print("Warning: 'image_format' not found in settings. Using default value '../step1-panorama-rendering/output_color/*.png'.")
            self.settings['image_format'] = '../step1-panorama-rendering/output_color/*.png' 
        if not 'output_width' in self.settings: 
            print("Warning: 'output_width' not found in settings. Using default value 1920.")
            self.settings['output_width'] = 1920
        if not 'output_height' in self.settings:
            print("Warning: 'output_height' not found in settings. Using default value 1080.")
            self.settings ['output_height'] = 1080
        if not 'interommatidial_angle' in self.settings:
            self.settings['interommatidial_angle'] = 1.5
        if not 'ommatidium_angle' in self.settings:
            print("Warning: 'ommatidium_angle' not found in settings. Using default value 15.")
            self.settings['ommatidium_angle'] = 15
        if not 'ommatidium_count' in self.settings:
            print("Warning: 'ommatidium_count' not found in settings. Using default value 25.")
            self.settings['ommatidium_count'] = 25
        if not 'theta' in self.settings:
            print ("Warning: 'theta' not found in settings. Using default value 0.")
            self.settings['theta'] = 0
        if not 'phi' in self.settings:
            print ("Warning: 'phi' not found in settings. Using default value 0.")
            self.settings['phi'] = 0
        if not 'filter' in self.settings:
            print ("Warning: 'filter' not found in settings. Using default value 'hexagonal_depth_gaussian'.")
            self.settings['filter'] = 'hexagonal_depth_gaussian'
        if not 'view_mode' in self.settings:
            print( "Warning: 'view_mode' not found in settings. Using default value 'color'.")
            self.settings['view_mode'] = 'color'
        if not 'debug_mode' in self.settings:
            print ("Warning: 'debug_mode' not found in settings. Using default value False.")
            self.settings['debug_mode'] = False
        if not 'blur_size' in self.settings:
            print ("Warning: 'blur_size' not found in settings. Using default value 30.")
            self.settings['blur_size'] = 30

        self.pre_setup  = True
        self.view_image = None

        image_format  = self.settings['image_format']  
        # 画像の読み込み
        self.image_files = sorted(glob.glob(image_format))
        self.current_image_index = 0
        self.panorama = cv2.imread(self.image_files[self.current_image_index])

        # Depthファイルのパスを生成
        depth_format = image_format.replace('output_color', 'output_depth').replace('.png', '.exr')
        self.depth_files = sorted(glob.glob(depth_format))

        self.screen_width = 1366
        self.screen_height = 768

        self.master = master
        # tkinterの仕様上, 画面サイズより大きい領域は自動的に切り取られるため, 画面サイズを取得
        output_width  = self.settings['output_width']
        output_height = self.settings['output_height']
        geometry_str = f"{self.screen_width}x{self.screen_height}"
        self.master.geometry(geometry_str)
        self.master.title("Parameter UI")
        self.master.bind("<Configure>", self.on_resize)
        self.master.bind("<Escape>"   , self.on_esc_key)
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)

        # 画面全体を覆うimageを作成
        image_bgr        = np.zeros((output_height, output_width, 3), np.uint8)
        image_rgb        = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        self.image_pil   = Image.fromarray(image_rgb)
        self.image_pil   = self.image_pil.resize ((self.screen_width, self.screen_height))
        self.image_tk    = ImageTk.PhotoImage(self.image_pil)
        self.canvas      = tk.Canvas(self.master, width=self.screen_width, height=self.screen_height)
        self.canvas.pack()
        self.imageItemID = self.canvas.create_image(0, 0, image=self.image_tk, anchor='nw')
        # # UIフレームを作成
        self.ui_frame    = tk.Frame(self.master)
        self.ui_frame.place(x=0, y=0, width=self.screen_width/7, height=self.screen_height/2)
        self.ui_frame_is_focused = False

        self.ui_input_interommatidial_angle = tk.StringVar()
        self.ui_input_ommatidium_angle      = tk.StringVar()
        self.ui_input_ommatidium_count      = tk.StringVar()
        self.ui_input_filter                = tk.StringVar()

        # titleは現在のフレーム番号/総フレーム数
        self.update_title()

        self.setup_ui()

    def setup_ui(self):
        interommatidial_angle_label = tk.Label(self.ui_frame, text="個眼間画角")
        interommatidial_angle_entry = tk.Entry(self.ui_frame, textvariable=self.ui_input_interommatidial_angle)
        interommatidial_angle_label.grid(row=0, column=0, columnspan=3)
        interommatidial_angle_entry.grid(row=1, column=0, columnspan=3)
        interommatidial_angle_entry.insert (0, self.settings['interommatidial_angle'])

        ommatidium_angle_label = tk.Label(self.ui_frame, text="個眼視野角")
        ommatidium_angle_entry = tk.Entry(self.ui_frame, textvariable=self.ui_input_ommatidium_angle)
        ommatidium_angle_label.grid(row=2, column=0, columnspan=3)
        ommatidium_angle_entry.grid(row=3, column=0, columnspan=3)
        ommatidium_angle_entry.insert (0, self.settings['ommatidium_angle'])

        ommatidium_count_label = tk.Label(self.ui_frame, text="個眼個数")
        ommatidium_count_entry = tk.Entry(self.ui_frame, textvariable=self.ui_input_ommatidium_count)
        ommatidium_count_label.grid(row=4, column=0, columnspan=3)
        ommatidium_count_entry.grid(row=5, column=0, columnspan=3)
        ommatidium_count_entry.insert (0, self.settings['ommatidium_count'])

        filter_label = tk.Label(self.ui_frame, text="フィルタ切り替え")
        filter_combobox = ttk.Combobox(self.ui_frame, values=["none","hexagonal", "hexagonal_gaussian", "hexagonal_depth_gaussian","debug_color","debug_depth"], textvariable=self.ui_input_filter)
        filter_combobox.set (self.settings['filter'])
        filter_label.grid(row=6, column=0, columnspan=3)
        filter_combobox.grid(row=7, column=0, columnspan=3)

        apply_button = tk.Button(self.ui_frame, text="変更の適用", command=self.on_apply_click)
        apply_button.grid(row=8, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)

        view_control_label = tk.Label(self.ui_frame, text="視点操作(上下左右)")
        view_control_label.grid(row=9, column=0, columnspan=3)

        up_button = tk.Button(self.ui_frame, text="上", command=self.on_up_click)
        down_button = tk.Button(self.ui_frame, text="下", command=self.on_down_click)
        left_button = tk.Button(self.ui_frame, text="左", command=self.on_left_click)
        right_button = tk.Button(self.ui_frame, text="右", command=self.on_right_click)
        up_button.grid(row=10, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        left_button.grid(row=11, column=0, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        down_button.grid(row=11, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        right_button.grid(row=11, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)


        move_image_label = tk.Label(self.ui_frame, text="画像の変更(+1, -1, +10, -10)")
        move_image_label.grid(row=12, column=0, columnspan=3)

        prev_1frame_image_button = tk.Button(self.ui_frame, text="前の画像(-1)", command=self.on_prev_1frame_image)
        prev_1frame_image_button.grid(row=13, column=0, columnspan=1,  sticky=tk.N+tk.S+tk.E+tk.W)
        next_1frame_image_button = tk.Button(self.ui_frame, text="次の画像(+1)", command=self.on_next_1frame_image)
        next_1frame_image_button.grid(row=13, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)

        prev_10frame_image_button = tk.Button(self.ui_frame, text="前の画像(-10)", command=self.on_prev_10frame_image)
        prev_10frame_image_button.grid(row=14, column=0, columnspan=1,  sticky=tk.N+tk.S+tk.E+tk.W)
        next_10frame_image_button = tk.Button(self.ui_frame, text="次の画像(+10)", command=self.on_next_10frame_image)
        next_10frame_image_button.grid(row=14, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)


        save_view_image_button = tk.Button(self.ui_frame, text="現在の視点画像を保存", command=self.on_save_view_image_click)
        save_view_image_button.grid(row=15, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)

        save_settings_button = tk.Button(self.ui_frame, text="設定ファイル保存(.toml)", command=self.on_save_settings_click)
        save_settings_button.grid(row=16, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        
    def run(self):
        self.update_view()
        self.master.mainloop()
        self.save_settings()

    def on_apply_click(self):
        new_interommatidial_angle = float(self.ui_input_interommatidial_angle.get())
        new_ommatidium_angle      = float(self.ui_input_ommatidium_angle.get())
        new_ommatidium_count      = int(self.ui_input_ommatidium_count.get())
        new_filter                = self.ui_input_filter.get()
        should_update = False
        if self.settings['interommatidial_angle'] != new_interommatidial_angle:
            self.settings['interommatidial_angle'] = new_interommatidial_angle
            should_update = True
        if self.settings['ommatidium_angle'] != new_ommatidium_angle:
            self.settings['ommatidium_angle'] = new_ommatidium_angle
            should_update = True
        if self.settings['ommatidium_count'] != new_ommatidium_count:
            self.settings['ommatidium_count'] = new_ommatidium_count
            should_update = True
        if new_filter == 'debug_color':
            if self.settings['debug_mode'] != True:
                self.settings['debug_mode'] = True
                self.settings['view_mode'] = 'color'
                should_update = True
            elif self.settings['view_mode'] != 'color':
                self.settings['view_mode'] = 'color'
                should_update = True
        elif new_filter == 'debug_depth':
            if self.settings['debug_mode'] != True:
                self.settings['debug_mode'] = True
                self.settings['view_mode'] = 'depth'
                should_update = True
            elif self.settings['view_mode'] != 'depth':
                self.settings['view_mode'] = 'depth'
                should_update = True
        else:
            if self.settings['filter'] != new_filter:
                self.settings['view_mode'] = 'color'
                self.settings['filter'] = new_filter
                self.settings['debug_mode'] = False
                should_update = True
            elif self.settings['debug_mode']:
                self.settings['debug_mode'] = False
                should_update = True
            elif self.settings['view_mode'] != 'color':
                self.settings['view_mode'] = 'color'
                should_update = True

        if should_update:
            print("変更を適用します")
            print("個眼間画角: ", self.ui_input_interommatidial_angle.get())
            print("個眼視野角: ", self.ui_input_ommatidium_angle.get())
            print("個眼個数: ", self.ui_input_ommatidium_count.get())
            print("フィルタ: ", self.ui_input_filter.get())
            self.update_view()

    def on_up_click(self):
        self.settings['phi'] = min(self.settings['phi'] + 5, 90)
        print(f"event.char: W - Rotate up, Phi: {self.settings['phi']}")
        self.update_view()

    def on_down_click(self):
        self.settings['phi'] = max(self.settings['phi'] - 5, -90)
        print(f"event.char: S - Rotate down, Phi: {self.settings['phi']}")
        self.update_view()

    def on_left_click(self):
        self.settings['theta'] = (self.settings['theta'] + 10) % 360
        print(f"event.char: A - Rotate left, Theta: {self.settings['theta']}")
        self.update_view()

    def on_right_click(self):
        self.settings['theta'] = (self.settings['theta'] - 10) % 360
        print(f"event.char: D - Rotate right, Theta: {self.settings['theta']}")
        self.update_view()

    def on_save_view_image_click(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
        )
        if not file_path:
            print("保存がキャンセルされました。")
            return
        cv2.imwrite(file_path, self.view_image)
        print("現在の視点画像を保存しました: ", file_path.split('/')[-1])

    def on_save_settings_click(self):
        self.save_settings()

    def on_resize(self, event):
        cur_width = self.master.winfo_width()
        cur_height = self.master.winfo_height()
        if cur_width != self.settings['output_width'] or cur_height != self.settings['output_height']:
            if self.pre_setup:
                return
            print (f"表示画面サイズが変更されました: {cur_width}x{cur_height}")
            self.screen_width  = cur_width
            self.screen_height = cur_height
            self.update_canvas_from_pil()
        else:
            if self.pre_setup:
                self.pre_setup = False

    def on_next_1frame_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        print(f"event.char: ] - Next image, Index: {self.current_image_index}")
        self.update_view()
        self.update_title()

    def on_prev_1frame_image(self):
        if self.current_image_index == 0:
            return
        self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
        print(f"event.char: [ - Previous image, Index: {self.current_image_index}")
        self.update_view()
        self.update_title()

    def on_next_10frame_image(self):
        self.current_image_index = (self.current_image_index + 10) % len(self.image_files)
        print(f"event.char: Shift+] - Forward 10 frames, Index: {self.current_image_index}")
        self.update_view()
        self.update_title()
    
    def on_prev_10frame_image(self):
        if self.current_image_index < 10:
            return
        self.current_image_index = (self.current_image_index - 10) % len(self.image_files)
        print(f"event.char: Shift+[ - Backward 10 frames, Index: {self.current_image_index}")
        self.update_view()
        self.update_title()

    def on_esc_key(self, event):
        print("ESCキーが押されました, 終了します")
        self.master.quit()
    
    def save_settings(self):
        # scriptのworking directoryを取得
        working_directory = os.getcwd()
        # 保存ファイル名は, settings_YYYYMMDDHHMMSS.toml
        save_file_name = working_directory+f"/settings_{time.strftime('%Y%m%d%H%M%S')}.toml"
        # settingsを保存
        with open(save_file_name, 'wb') as file:
            tomli_w.dump(self.settings, file)
            print(f"設定ファイルを保存しました: {save_file_name.split('/')[-1]}")

    def update_view(self):
        (tmp_panorama,tmp_view_image) = update_view_process(self.current_image_index, self.image_files, self.depth_files, self.settings, False,False)
        self.panorama    = tmp_panorama
        self.view_image  = tmp_view_image 
        image_bgr        = self.view_image
        image_rgb        = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        self.image_pil   = Image.fromarray(image_rgb)
        self.update_canvas_from_pil()

    def update_canvas_from_pil(self):
        self.image_pil   = self.image_pil.resize((self.screen_width, self.screen_height))
        self.image_tk    = ImageTk.PhotoImage(self.image_pil)
        self.canvas.itemconfig(self.imageItemID, image=self.image_tk)

    def update_title(self):
        # titleは現在のフレーム番号/総フレーム数
        self.master.title(f"{self.current_image_index}/{len(self.image_files)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UIViewer(root)
    app.run()