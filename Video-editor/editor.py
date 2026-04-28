from moviepy import VideoFileClip
from pyray import *
from _cffi_backend import FFI
import numpy as np
from numpy import ndarray

HEIGHT = 1080
WIDTH = 1920
SCALE_FATOR = 0.8

video = VideoFileClip("sample.mp4")
video_width = video.size[0]
video_height = video.size[1]

def video_get_frame_at(video: VideoFileClip, frame: int) -> FFI.CData:
    frame_time = frame * (1 / video.fps)
    
    frame_rgb = video.get_frame(frame_time)
    
    frame_rgba = np.empty((video_height, video_width, 4), dtype=np.uint8)
    frame_rgba[..., :3] = frame_rgb.astype(np.uint8, copy=False)
    frame_rgba[..., 3] = 255
    frame_rgba = np.ascontiguousarray(frame_rgba)
    
    return ffi.new('char []', frame_rgba.tobytes(order="C"))

set_config_flags(ConfigFlags.FLAG_WINDOW_RESIZABLE)
init_window(int(WIDTH*SCALE_FATOR), int(HEIGHT*SCALE_FATOR), "Video Editor - Python")

set_target_fps(60)

rimg = gen_image_color(video_width, video_height, BLANK)
tex = load_texture_from_image(rimg)
unload_image(rimg)

while not window_should_close():
    begin_drawing()
    frame = video_get_frame_at(video, 0)
    update_texture(tex, frame)
    clear_background((10, 10, 20))
    
    
    draw_texture(tex, 0, 0, WHITE)
     
    end_drawing()

unload_texture(tex)
close_window()