from pyray import *

HEIGHT = 1080
WIDTH = 1920
SCALE_FATOR = 0.8

set_config_flags(ConfigFlags.FLAG_WINDOW_RESIZABLE)
init_window(int(WIDTH*SCALE_FATOR), int(HEIGHT*SCALE_FATOR), "Video Editor - Python")

while not window_should_close():
    begin_drawing()
    
    clear_background((10, 10, 20))
    
    draw_text("Hello world", 190, 200, 20, VIOLET)
    end_drawing()
close_window()