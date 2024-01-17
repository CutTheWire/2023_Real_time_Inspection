import cv2
import time
import os
import sys
import subprocess

ASCII_CHARS = '⩷⁜⁙⁎+⁘⁖‥· '

def map_pixels_to_ascii(image, ascii_chars):
    ascii_str = ''
    for pixel_value in image.flatten():
        ascii_str += ascii_chars[pixel_value * len(ascii_chars) // 256]
    return ascii_str

def print_ascii_art(ascii_str, frame_width):
    ascii_art = ''
    for i in range(0, len(ascii_str), frame_width):
        ascii_art += ascii_str[i:i+frame_width] + '\n'
    return ascii_art

def move_cursor_to_top_left():
    print("\033[H", end='')

if __name__ == '__main__':
    if "run_in_new_window" not in sys.argv:
        script_path = os.path.abspath(__file__)
        subprocess.run(f'start cmd /c python "{script_path}" run_in_new_window', shell=True)
    else:
        cap = cv2.VideoCapture(0)
        try:
            # 첫 프레임을 출력하기 전에 커서를 화면 맨 위로 이동.
            move_cursor_to_top_left()
            while True:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame = cv2.resize(frame, (400, 120))
                    ascii_str = map_pixels_to_ascii(frame, ASCII_CHARS)
                    ascii_art = print_ascii_art(ascii_str, frame.shape[1])

                    # 커서를 화면 맨 위로 이동
                    move_cursor_to_top_left()
                    print(ascii_art, end='')

                    time.sleep(0.01)
        finally:
            cap.release()
