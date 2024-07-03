import sys
import os
file_paths = ["./settings/settings0.toml" , "./settings/settings1.toml" , "./settings/settings2.toml"]
modes = ["none", "hexagonal_gaussian", "hexagonal_depth_gaussian", "debug"]
for file_path in file_paths:
    # file_path = "./settings/settings0.toml"
    # new directory = "./settings/settings0_modifiers"
    new_directory = file_path.replace(".toml", "_modifiers")
    # make new directory
    os.makedirs(new_directory, exist_ok=True)
    # settings0.tomlを読む
    with open(file_path, "r", encoding="utf-8") as f:
        in_settings = f.read()
        # コメントを削除
        in_settings = in_settings.split("\n")
        in_settings = [s.split("#")[0] for s in in_settings]
        in_settings = "\n".join(in_settings)
        # settings0.tomlを文字列として書き換える
        # filter="none"
        # filter="hexagonal_gaussian"
        # filter="hexagonal_depth_gaussian"
        # debug_mode = True
        # 書き換えた結果をそれぞれ
        # settings0_modifiers/settings0_filter_none.toml
        # settings0_modifiers/settings0_filter_hexagonal_gaussian.toml
        # settings0_modifiers/settings0_filter_hexagonal_depth_gaussian.toml
        # settings0_modifiers/settings0_filter_debug.toml
        # に保存する
        # その際, コメント(#以下の文字列)は削除する
        # settings1, settings2についても同様の処理を行う
        for mode in modes:
            settings = str(in_settings)
            
            if mode == "debug":
                # 置換を行う
                settings = settings.replace("debug_mode = false", "debug_mode = true")
                print("debug_mode = true")
            elif mode == "none":
                # 置換を行う
                settings = settings.replace("filter = \"none\"", "filter = \"{}\"".format(mode))
                print ("filter = \"{}\"".format(mode))
            elif mode == "hexagonal_gaussian":
                # 置換を行う
                settings = settings.replace("filter = \"none\"", "filter = \"{}\"".format(mode))
                print ("filter = \"{}\"".format(mode))
            elif mode == "hexagonal_depth_gaussian":
                # 置換を行う
                settings = settings.replace("filter = \"none\"", "filter = \"{}\"".format(mode))
                print ("filter = \"{}\"".format(mode))
            # ファイル名を作成
            file_base = file_path.split("/")[-1]
            print ("file_base: ", file_base)
            new_file_path = os.path.join( new_directory, file_base.replace(".toml", "_filter_{}.toml".format(mode)) )
            with open(new_file_path, "w") as f:
                f.write(settings)
            # code/image_batch_generator.pyを引数付きで実行
            # python code/image_batch_generator.py -f settings/settings0_modifiers/settings0_filter_none.toml
            # 他についても同様
            os.system("python code/image_batch_generator.py -f {}".format(new_file_path))
            cur_outputpath = "./output_{}".format(mode)
            # SET ffmpeg=..\thirdparty\ffmpeg-7.0.1-essentials_build\bin\ffmpeg.exe
            # %ffmpeg% -r 30 -i output_hexagonal_depth_gaussian\Image%%04d_hexagonal_depth_gaussian.png -c:v libx264 -pix_fmt yuv420p output_hexagonal_depth_gaussian.mp4
            ffmpeg = "..\\thirdparty\\ffmpeg-7.0.1-essentials_build\\bin\\ffmpeg.exe"
            cmd = "{} -r 30 -i {}\\Image%04d_{}.png -c:v libx264 -pix_fmt yuv420p {}_{}.mp4".format(ffmpeg, cur_outputpath, mode,new_directory+ "/output", mode)
            print (cmd)
            os.system(cmd)
