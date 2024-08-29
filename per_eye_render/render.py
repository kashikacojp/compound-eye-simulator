import os
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from step1_calculate_pixel_viewport.code import calculate_pixel_viewport
from step2_batch_eye_rendering.code      import scene_renderer
from step3_apply_hexigonal_filter.code   import apply_hexigonal_filter

def show_result_image(path,settings):
    class ImageApp:
        def __init__(self, master, image):
            self.master = master
            self.master.title("Image Viewer")

            # 画像のサイズを取得
            self.original_image = image
            self.height, self.width, _ = self.original_image.shape

            # アスペクト比を保ちながら横幅を800にリサイズ
            self.new_width = 800
            self.new_height = int((self.new_width / self.width) * self.height)
            self.resized_image = cv2.resize(self.original_image, (self.new_width, self.new_height))

            # OpenCVの画像をPILの画像に変換
            self.image_pil = Image.fromarray(cv2.cvtColor(self.resized_image, cv2.COLOR_BGR2RGB))
            self.image_tk = ImageTk.PhotoImage(self.image_pil)

            # キャンバスを作成して画像を表示
            self.canvas = tk.Canvas(self.master, width=self.new_width, height=self.new_height)
            self.canvas.pack()
            self.imageItemID = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

            # ボタンを作成して配置
            self.save_button = tk.Button(self.master, text="画像を保存", command=self.save_image)
            self.save_button.pack(side=tk.BOTTOM)
        def update_canvas_from_pil(self):
            self.image_pil = self.image_pil.resize((self.new_width, self.new_height))
            self.image_tk = ImageTk.PhotoImage(self.image_pil)
            self.canvas.itemconfig(self.imageItemID, image=self.image_tk)

        def save_image(self):
            # ファイルダイアログを開いて保存先を選択
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png", 
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp")],
                initialdir=os.getcwd()
            )
            if save_path:
                cv2.imwrite(save_path, image)
                # 日本語に直す
                # messagebox.showinfo("Image Saved", f"Image saved to {save_path}")
                messagebox.showinfo("save_image", f"画像を{save_path}に保存しました")
    image = cv2.imread(path)
    if settings["clipping"]:           
        output_width = settings["output_width"]
        ommatidium_count = settings["ommatidium_count"]
        new_output_width = output_width *(ommatidium_count-0.5) / ommatidium_count
        new_output_width = int(new_output_width)
        new_output_height= settings["output_height"]
        image = image[0:new_output_height, 0:new_output_width]
    # Tkinterアプリケーションを作成して実行
    root = tk.Tk()
    app = ImageApp(root, image)
    root.mainloop()
    return

def rander_frame(settings):
    initial_debug_mode = settings['debug_mode']
    basedir = os.path.dirname(os.path.abspath(__file__))
    color_image_dir = os.path.join(basedir,"output","temp_color_image", "radius"+str(settings["ommatidium_radius"]),"frame"+str(settings["frame"]))
    depth_image_dir = os.path.join(basedir,"output","temp_depth_image", "radius"+str(settings["ommatidium_radius"]),"frame"+str(settings["frame"]))
    output_dir = os.path.join(basedir,"output")
    print(color_image_dir)
    print(output_dir)
    if not os.path.exists(color_image_dir):
        os.makedirs(color_image_dir)
    if not os.path.exists(depth_image_dir):
        os.makedirs(depth_image_dir)
    hex_pos_setting = calculate_pixel_viewport.run(settings)
    scene_path = settings["scene_path"]
    frame_index = settings["frame"]
    scene_renderer.run(scene_path, hex_pos_setting, color_image_dir,depth_image_dir,frame_index) # Generate Images in output_color/output_depth folder
    settings['debug_mode'] = False
    apply_hexigonal_filter.run(settings,color_image_dir, output_dir,frame_index) # Generate Images in output_color/output_depth folder
    settings['debug_mode'] = True
    apply_hexigonal_filter.run(settings,color_image_dir, output_dir,frame_index) # Generate Images in output_color/output_depth folder
    radius = settings["ommatidium_radius"]
    # output_dirにradius=radiusのフォルダを作成
    radius_output_dir = os.path.join(output_dir, "radius="+str(radius), "frame"+str(frame_index))
    # output_dirにある全ての*.pngファイルをradius_output_dirに移動
    os.makedirs(radius_output_dir, exist_ok=True)
    for file in os.listdir(output_dir):
        if file.endswith(".png"):
            os.rename(os.path.join(output_dir, file), os.path.join(radius_output_dir, file))

    result_image_path = None
    for file in os.listdir(radius_output_dir):
        if file.endswith(".png"):
            if initial_debug_mode is True:
                if file.startswith("output_debug"):
                    result_image_path = os.path.join(radius_output_dir, file)
                    break
            else:
                if file.startswith("output_"+settings["filter"]):
                    result_image_path = os.path.join(radius_output_dir, file)
                    break
    if not result_image_path:
        raise Exception("Result image not found.")
    show_result_image(result_image_path,settings)

def render_animation(settings):
    # total_frame = 600
    # frames            = range(1, total_frame + 1, 3) 
    # for frame in frames:
    #     settings["frame"] = frame
    #     rander_frame(settings)
    
    # frames            = range(2, total_frame + 1, 3) 
    # for frame in frames:
    #     settings["frame"] = frame
    #     rander_frame(settings)

    # frames            = range(3, total_frame + 1, 3) 
    # for frame in frames:
    #     settings["frame"] = frame
    #     rander_frame(settings)
    rander_frame(settings)

# argparse
parser = argparse.ArgumentParser()
parser.add_argument("--setting", type=str, default="")
parser.add_argument("--scene_path", type=str, default=settings["scene_path"])
parser.add_argument("--output_width", type=int, default=settings["output_width"])
parser.add_argument("--output_height", type=int, default=settings["output_height"])
parser.add_argument("--image_format", type=str, default=settings["image_format"])
parser.add_argument("--interommatidial_angle", type=float, default=settings["interommatidial_angle"])
parser.add_argument("--ommatidium_angle", type=float, default=settings["ommatidium_angle"])
parser.add_argument("--ommatidium_count", type=int, default=settings["ommatidium_count"])
parser.add_argument("--ommatidium_radius", type=float, default=settings["ommatidium_radius"])
parser.add_argument("--theta", type=float, default=settings["theta"])
parser.add_argument("--phi", type=float, default=settings["phi"])
parser.add_argument("--filter", type=str, default=settings["filter"])
parser.add_argument("--view_mode", type=str, default=settings["view_mode"])
parser.add_argument("--debug_mode", action="store_true")
parser.add_argument("--blur_size", type=int, default=settings["blur_size"])
parser.add_argument("--frame", type=int, default=settings["frame"])
parser.add_argument("--clipping", action="store_true")
args = parser.parse_args()

if args.setting != "":
    with open(args.setting,mode='rb') as file:
        if not file:
            print(f"Error: Could not open file {args.setting}")
            exit()
        settings = tomllib.load(file)
settings["scene_path"]           = args.scene_path
settings["output_width"]         = args.output_width
settings["output_height"]        = args.output_height
settings["image_format"]         = args.image_format
settings["interommatidial_angle"]= args.interommatidial_angle
settings["ommatidium_angle"]     = args.ommatidium_angle
settings["ommatidium_count"]     = args.ommatidium_count
settings["ommatidium_radius"]    = args.ommatidium_radius
settings["theta"]                = args.theta
settings["phi"]                  = args.phi
settings["filter"]               = args.filter
settings["view_mode"]            = args.view_mode
settings["debug_mode"]           = args.debug_mode
settings["blur_size"]            = args.blur_size
settings["frame"]                = args.frame
settings["clipping"]             = args.clipping
print (settings)
render_animation(settings)
