SET ffmpeg=..\thirdparty\ffmpeg-7.0.1-essentials_build\bin\ffmpeg.exe
%ffmpeg% -r 30 -i output_hexagonal_depth_gaussian\Image%%04d_hexagonal_depth_gaussian.png -c:v libx264 -pix_fmt yuv420p output_hexagonal_depth_gaussian.mp4