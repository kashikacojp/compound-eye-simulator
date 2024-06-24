SET ffmpeg=..\thirdparty\ffmpeg-7.0.1-essentials_build\bin\ffmpeg.exe

REM Generate video with mp4 file with windows compatible format.
REM input: output_color/Image*.png
REM output: test_output_color.mp
REM setting: yuv, pix_fmt, and so on
%ffmpeg% -r 15 -i output_color\Image%%04d.png -c:v libx264 -pix_fmt yuv420p output_color.mp4

REM Generate video with mp4 file with windows compatible format.
REM input: output_depth/Image*.png
REM output: test_output_depth.mp
REM setting: yuv, pix_fmt, and so on
%ffmpeg% -r 15 -i output_depth\Image%%04d.png -c:v libx264 -pix_fmt yuv420p output_depth.mp4
