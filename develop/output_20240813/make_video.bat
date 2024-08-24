set FFMPEG=%~dp0../ffmpeg-7.0.2/bin/ffmpeg.exe

set NAME=tmp_radius=0.0
%FFMPEG% -framerate 10 -i %NAME%/output_hexagonal_depth_gaussian_%%04d.png -c:v libx264 -pix_fmt yuv420p -crf 22 %NAME%_video.mp4

set NAME=tmp_radius=0.005
%FFMPEG% -framerate 10 -i %NAME%/output_hexagonal_depth_gaussian_%%04d.png -c:v libx264 -pix_fmt yuv420p -crf 22 %NAME%_video.mp4