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
import subprocess
from PIL import Image, ImageTk
from update_view_process import update_view_process

class UIViewer:
    def __init__(self, master):
        parser = argparse.ArgumentParser(description='360 Viewer for compound eye simulator')
        prompt = "TOML settings file (e.g., 'settings/*.toml'): "
        default = './settings/settings.toml'
        parser.add_argument('-s','--setting', type=str, default=default, help=f"{prompt} (default: {default}): ")
        args = parser.parse_args()
        with open(args.setting,mode='rb') as file:
            if not file:
                print(f"Error: Could not open file {args.setting}")
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
        if not 'frame' in self.settings:
            print ("Warning: 'frame' not found in settings. Using default value 0.")
            self.settings['frame'] = 0

        self.pre_setup  = True
        self.view_image = None

        image_format  = self.settings['image_format']  
        # 画像の読み込み
        self.image_files = sorted(glob.glob(image_format))
        if len(self.image_files) == 0:
            print(f"No images found: {image_format}")
            sys.exit(1)
        if len(self.image_files) <= int(self.settings['frame']):
            print(f"Num images not matched with current frame number: {len(self.image_files)} <= {self.settings['frame']}")
            self.settings['frame'] = 0
        self.panorama = cv2.imread(self.image_files[self.settings['frame']])

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
        self.ui_frame.place(x=0, y=0, width=self.screen_width/7, height=self.screen_height*0.8)
        self.ui_frame_is_focused = False

        self.ui_input_interommatidial_angle = tk.StringVar()
        self.ui_input_ommatidium_angle      = tk.StringVar()
        self.ui_input_ommatidium_count      = tk.StringVar()
        self.ui_input_frame                 = tk.StringVar()
        self.ui_input_filter                = tk.StringVar()
        self.ui_blur_size                   = tk.DoubleVar()

        # titleは現在のフレーム番号/総フレーム数
        self.update_title()

        self.setup_ui()

    def setup_ui(self):
        row_idx = 0
        interommatidial_angle_label = tk.Label(self.ui_frame, text="個眼間角度")
        interommatidial_angle_entry = tk.Entry(self.ui_frame, textvariable=self.ui_input_interommatidial_angle)
        interommatidial_angle_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        interommatidial_angle_entry.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        interommatidial_angle_entry.insert (0, self.settings['interommatidial_angle'])

        ommatidium_angle_label = tk.Label(self.ui_frame, text="個眼視野角")
        ommatidium_angle_entry = tk.Entry(self.ui_frame, textvariable=self.ui_input_ommatidium_angle)
        ommatidium_angle_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        ommatidium_angle_entry.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        ommatidium_angle_entry.insert (0, self.settings['ommatidium_angle'])

        ommatidium_count_label = tk.Label(self.ui_frame, text="個眼個数")
        ommatidium_count_entry = tk.Entry(self.ui_frame, textvariable=self.ui_input_ommatidium_count)
        ommatidium_count_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        ommatidium_count_entry.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        ommatidium_count_entry.insert (0, self.settings['ommatidium_count'])

        filter_label = tk.Label(self.ui_frame, text="フィルタ切り替え")
        #filter_combobox = ttk.Combobox(self.ui_frame, values=["none","hexagonal", "hexagonal_gaussian", "hexagonal_depth_gaussian","debug_color","debug_depth"], textvariable=self.ui_input_filter)
        filter_combobox = ttk.Combobox(self.ui_frame, values=[self.convert_filter_name_reverse("none"),self.convert_filter_name_reverse("hexagonal"), self.convert_filter_name_reverse("hexagonal_depth_gaussian")], textvariable=self.ui_input_filter)
        filter_combobox.set (self.convert_filter_name_reverse(self.settings['filter']))
        filter_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        filter_combobox.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1

        blur_label = tk.Label(self.ui_frame, text="ぼかしサイズ")
        blur_slider = tk.Scale(self.ui_frame, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.ui_blur_size)
        blur_slider.set(0.5)
        blur_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        blur_slider.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1

        apply_button = tk.Button(self.ui_frame, text="変更の適用", command=self.on_apply_click)
        apply_button.grid(row=row_idx, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        view_control_label = tk.Label(self.ui_frame, text="視点操作(上下左右)")
        view_control_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1

        up_button = tk.Button(self.ui_frame, text="上", command=self.on_up_click)
        down_button = tk.Button(self.ui_frame, text="下", command=self.on_down_click)
        left_button = tk.Button(self.ui_frame, text="左", command=self.on_left_click)
        right_button = tk.Button(self.ui_frame, text="右", command=self.on_right_click)
        up_button.grid(row=row_idx, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1
        left_button.grid(row=row_idx, column=0, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        down_button.grid(row=row_idx, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        right_button.grid(row=row_idx, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        frame_count_label = tk.Label(self.ui_frame, text="フレーム番号")
        frame_count_entry = tk.Entry(self.ui_frame, textvariable=self.ui_input_frame)
        frame_count_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        frame_count_entry.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1
        frame_count_entry.insert (0, self.settings['frame'])

        apply_frame_button = tk.Button(self.ui_frame, text="変更の適用", command=self.on_apply_frame_click)
        apply_frame_button.grid(row=row_idx, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        move_image_label = tk.Label(self.ui_frame, text="画像の変更(+1, -1, +10, -10)")
        move_image_label.grid(row=row_idx, column=0, columnspan=3)
        row_idx = row_idx + 1

        prev_1frame_image_button = tk.Button(self.ui_frame, text="前の画像(-1)", command=self.on_prev_1frame_image)
        prev_1frame_image_button.grid(row=row_idx, column=0, columnspan=1,  sticky=tk.N+tk.S+tk.E+tk.W)
        next_1frame_image_button = tk.Button(self.ui_frame, text="次の画像(+1)", command=self.on_next_1frame_image)
        next_1frame_image_button.grid(row=row_idx, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        prev_10frame_image_button = tk.Button(self.ui_frame, text="前の画像(-10)", command=self.on_prev_10frame_image)
        prev_10frame_image_button.grid(row=row_idx, column=0, columnspan=1,  sticky=tk.N+tk.S+tk.E+tk.W)
        next_10frame_image_button = tk.Button(self.ui_frame, text="次の画像(+10)", command=self.on_next_10frame_image)
        next_10frame_image_button.grid(row=row_idx, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        save_view_image_button = tk.Button(self.ui_frame, text="現在の視点画像を保存", command=self.on_save_view_image_click)
        save_view_image_button.grid(row=row_idx, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        load_settings_button = tk.Button(self.ui_frame, text="設定ファイル読み込み(.toml)", command=self.on_load_settings_click)
        load_settings_button.grid(row=row_idx, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        save_settings_button = tk.Button(self.ui_frame, text="設定ファイル保存(.toml)", command=self.on_save_settings_click)
        save_settings_button.grid(row=row_idx, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1

        run_ommatidium_button = tk.Button(self.ui_frame, text="個眼毎にレンダリング", command=self.on_run_ommatidium_click)
        run_ommatidium_button.grid(row=row_idx, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        row_idx = row_idx + 1
        
    def run(self):
        self.update_view()
        self.master.mainloop()
        print("[終了時の設定]\n" + tomli_w.dumps(self.settings))

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
            new_filter = self.convert_filter_name(new_filter)

            if new_filter == "":
                print("フィルタが不正です")
                return

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

        if self.update_blur_size(float(self.ui_blur_size.get())):
            should_update = True

        if should_update:
            self.update_view()

    def on_apply_frame_click(self):
        new_frame = int(self.ui_input_frame.get())
        if new_frame != self.settings['frame']:
            self.settings['frame'] = new_frame
            self.update_view()
            self.update_title()

    def update_blur_size(self, value):
        hex_width = 1920 / int(self.ui_input_ommatidium_count.get())
        blur_size = int(value * hex_width)
        if self.settings['blur_size'] == blur_size:
            return False
        else:
            self.settings['blur_size'] = blur_size
            return True

    def convert_filter_name(self, value):
        new_str = ""
        if value == "入力画像":
            new_str = "none"            
        elif value == "平均フィルタ":
            new_str = "hexagonal"
        elif value == "深度+ガウシアンフィルタ":
            new_str = "hexagonal_depth_gaussian"           
        return new_str

    def convert_filter_name_reverse(self, value):
        new_str = ""
        if value == "none":
            new_str = "入力画像"
        elif value == "hexagonal":
            new_str = "平均フィルタ"
        elif value == "hexagonal_depth_gaussian":
            new_str = "深度+ガウシアンフィルタ"
        return new_str

    def on_up_click(self):
        self.settings['phi'] = min(self.settings['phi'] + 5, 90)
        #print(f"event.char: W - Rotate up, Phi: {self.settings['phi']}")
        self.update_view()

    def on_down_click(self):
        self.settings['phi'] = max(self.settings['phi'] - 5, -90)
        #print(f"event.char: S - Rotate down, Phi: {self.settings['phi']}")
        self.update_view()

    def on_left_click(self):
        self.settings['theta'] = (self.settings['theta'] + 10) % 360
        #print(f"event.char: A - Rotate left, Theta: {self.settings['theta']}")
        self.update_view()

    def on_right_click(self):
        self.settings['theta'] = (self.settings['theta'] - 10) % 360
        #print(f"event.char: D - Rotate right, Theta: {self.settings['theta']}")
        self.update_view()

    def on_save_view_image_click(self):
        root = tk.Tk()
        root.withdraw()
        #image_[phi]_[theta]_[フレーム番号]_[YYYYMMDDhhmmss].png　
        default_filename = f"image_{self.settings['phi']}_{self.settings['theta']}_{self.settings['frame']}_{time.strftime('%Y%m%d%H%M%S')}.png"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            initialdir=os.getcwd(),
            initialfile=default_filename
        )
        if not file_path:
            print("保存がキャンセルされました。")
            return
        cv2.imwrite(file_path, self.view_image)
        print("現在の視点画像を保存しました: ", file_path.split('/')[-1])

    def on_save_settings_click(self):
        self.save_settings()

    def on_load_settings_click(self):
        self.load_settings()

    def on_run_ommatidium_click(self):
        cur_script_path = os.path.abspath(__file__)
        dst_script_path = os.path.normpath(os.path.join(os.path.dirname(cur_script_path), "..\\..\\..\\develop\\render.py"))
        params = ""
        if 'scene_path' in self.settings:
            params = params + f" --scene_path {self.settings['scene_path']}"
        if 'output_width' in self.settings:
            params = params + f" --output_width {self.settings['output_width']}"
        if 'output_height' in self.settings:
            params = params + f" --output_height {self.settings['output_height']}"
        if 'image_format' in self.settings:
            params = params + f" --image_format {self.settings['image_format']}"
        if 'interommatidial_angle' in self.settings:
            params = params + f" --interommatidial_angle {self.settings['interommatidial_angle']}"
        if 'ommatidium_angle' in self.settings:
            params = params + f" --ommatidium_angle {self.settings['ommatidium_angle']}"
        if 'ommatidium_count' in self.settings:
            params = params + f" --ommatidium_count {self.settings['ommatidium_count']}"
        if 'theta' in self.settings:
            params = params + f" --theta {self.settings['theta']}"
        if 'phi' in self.settings:
            params = params + f" --phi {self.settings['phi']}"
        if 'filter' in self.settings:
            params = params + f" --filter {self.settings['filter']}"
        if 'view_mode' in self.settings:
            params = params + f" --view_mode {self.settings['view_mode']}"
        if 'debug_mode' in self.settings:
            if self.settings['debug_mode']:
                params = params + " --debug_mode"
        if 'blur_size' in self.settings:
            params = params + f" --blur_size {self.settings['blur_size']}"
        if 'frame' in self.settings:
            params = params + f" --frame {self.settings['frame']}"
        if 'clipping' in self.settings:
            if self.settings['clipping']:
                params = params + " --clipping"
        else:
            params = params + " --clipping"
        print (f"実行コマンド: pipenv run python {dst_script_path} {params}")
        try:
            process = subprocess.Popen("pipenv run python " + dst_script_path + " " + params, shell=True)
        except Exception as e:
            print("Error: ", e)
            return

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
        self.settings['frame'] = (self.settings['frame'] + 1) % len(self.image_files)
        # print(f"event.char: ] - Next image, Index: {self.settings['frame']}")
        self.update_view()
        self.update_title()

    def on_prev_1frame_image(self):
        self.settings['frame'] = self.settings['frame'] - 1
        if self.settings['frame'] < 0:
            self.settings['frame'] = len(self.image_files) + self.settings['frame'] # 'frame' is negative so add it to the total number of images
        # print(f"event.char: [ - Previous image, Index: {self.settings['frame']}")
        self.update_view()
        self.update_title()

    def on_next_10frame_image(self):
        self.settings['frame'] = (self.settings['frame'] + 10) % len(self.image_files)
        # print(f"event.char: Shift+] - Forward 10 frames, Index: {self.settings['frame']}")
        self.update_view()
        self.update_title()
    
    def on_prev_10frame_image(self):
        self.settings['frame'] = self.settings['frame'] - 10
        if self.settings['frame'] < 0:
            self.settings['frame'] = len(self.image_files) + self.settings['frame'] # 'frame' is negative so add it to the total number of images
        # print(f"event.char: Shift+[ - Backward 10 frames, Index: {self.settings['frame']}")
        self.update_view()
        self.update_title()

    def on_esc_key(self, event):
        print("ESCキーが押されました, 終了します")
        self.master.quit()
    
    def save_settings(self):
        # scriptのworking directoryを取得
        working_directory = os.getcwd()
        # 保存ファイル名は, settings_YYYYMMDDHHMMSS.toml
        default_filename = f"settings_{time.strftime('%Y%m%d%H%M%S')}.toml"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".toml",
            filetypes=[("TOML files", "*.toml"), ("All files", "*.*")],
            initialdir=working_directory,
            initialfile=default_filename
        )
        if not file_path:
            print("保存がキャンセルされました。")
            return
        with open(file_path, 'wb') as f:
            tomli_w.dump(self.settings, f)
            print("設定ファイルを保存しました: ", file_path.split('/')[-1])

    def load_settings(self):
        # scriptのworking directoryを取得
        working_directory = os.getcwd()
        file_path = filedialog.askopenfilename(
            filetypes=[("TOML files", "*.toml"), ("All files", "*.*")],
            initialdir=working_directory
        )
        if not file_path:
            print("読み込みがキャンセルされました。")
            return
        with open(file_path, 'rb') as f:
            self.settings = tomllib.load(f)
            print("設定ファイルを読み込みました: ", file_path.split('/')[-1])
            self.update_view()
            self.update_title()

    def update_view(self):
        (tmp_panorama,tmp_view_image) = update_view_process(self.settings['frame'], self.image_files, self.depth_files, self.settings, False,False,True)
        self.panorama    = tmp_panorama
        self.view_image  = tmp_view_image 
        image_bgr        = self.view_image
        image_rgb        = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        self.image_pil   = Image.fromarray(image_rgb)
        self.update_canvas_from_pil()

        print("変更を適用します")
        print("個眼間角度: ", self.ui_input_interommatidial_angle.get())
        print("個眼視野角: ", self.ui_input_ommatidium_angle.get())
        print("個眼個数: ", self.ui_input_ommatidium_count.get())
        print("フィルタ: ", self.ui_input_filter.get())
        print("ぼかしサイズ: ", self.settings['blur_size'])
        print(f"視点: ({self.settings['phi']}, {self.settings['theta']})")

    def update_canvas_from_pil(self):
        self.image_pil   = self.image_pil.resize((self.screen_width, self.screen_height))
        self.image_tk    = ImageTk.PhotoImage(self.image_pil)
        self.canvas.itemconfig(self.imageItemID, image=self.image_tk)

    def update_title(self):
        # titleは現在のフレーム番号/総フレーム数
        self.master.title(f"{self.settings['frame']}/{len(self.image_files)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UIViewer(root)
    app.run()