import sys
import os
import signal
import numpy as np

import tkinter as tk
from tkinter import font
from tkinter import messagebox
from screeninfo import get_monitors

from IMG.IPP import ImageCV

import DATA.base64_data as B64D

class MainView:
    def __init__(self, root: tk.Tk, mvapp) -> None:
        if getattr(sys, 'frozen', False):
            # 애플리케이션이 번들링된 경우
            font_path = os.path.join(sys._MEIPASS, "BinggraeTaom.ttf")
        else:
            # 애플리케이션이 번들링되지 않고 스크립트로 실행되는 경우
            font_path = "./2_Function/Main/DATA/BinggraeTaom.ttf"
        
        # root style
        self.label_style ={
            'bg': '#232326',
            'fg': 'white',
            'font': font.Font(family=font_path, size=15) }
        
        self.text_label_style ={
            'bg': '#343437',
            'fg': 'white',
            'font': font.Font(family=font_path, size=45) }
        
        self.exit_label_style ={
            'bg': '#B43437',
            'fg': 'white',
            'font': font.Font(family=font_path, size=15) }

        self.back_style ={
            'bg' : '#343437' }
        
        self.root_style ={
            'bg' : '#565659' }

        # root 설정
        self.root = root
        self.root.title("TWCV")
        self.root.configure(self.root_style)
        self.root.state('zoomed')
        self.root.attributes('-fullscreen', True)
        
        monitors = get_monitors()
        self.screen_width, self.screen_height = monitors[0].width, monitors[0].height
        self.frame_width = self.screen_width // 3
        self.frame_height = self.screen_height // 20

        self.frame1 = tk.Frame(self.root, width=self.screen_width, height = self.frame_height)
        self.frame2 = tk.Frame(self.root, width=self.frame_width, height = (self.screen_height - self.frame_height))
        self.frame3 = tk.Frame(self.root, width=self.screen_width - self.frame_width, height = (self.screen_height - (self.frame_height*3)))
        self.frame4 = tk.Frame(self.root, width=self.screen_width - self.frame_width, height = self.frame_height)
        self.frame5 = tk.Frame(self.root, width=self.screen_width - self.frame_width, height = self.frame_height)

        # 그리드에 위젯을 배치합니다.
        self.frame1.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="new")
        self.frame2.grid(row=1, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.frame3.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.frame4.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.frame5.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

        # 그리드의 크기를 설정합니다.
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=10)
        self.root.grid_columnconfigure(1, weight=1)

        # GUI 생성
        self.exit_button = tk.Button(self.frame1, text="X", command=self.exit_clicked, width=3)
        self.LabelV = tk.Label(self.frame2)
        self.video_label_1 = tk.Label(self.LabelV)
        self.LabelV2 = tk.Label(self.frame3)
        self.video_label_2 = tk.Label(self.LabelV2)
        self.text_label = tk.Label(self.frame4, text="ㅤㅤ")
        self.TW_logo_image = tk.Label(self.frame5)
        
        image = tk.PhotoImage(data=B64D.logo_image_base64)
        # 디자인
        self.frame1.configure(self.back_style)
        self.frame2.configure(self.back_style)
        self.frame3.configure(self.back_style)
        self.frame4.configure(self.back_style)
        self.frame5.configure(self.root_style)

        self.exit_button.configure(self.exit_label_style)
        self.video_label_1.configure(self.back_style)
        self.video_label_2.configure(self.back_style)
        self.text_label.configure(self.text_label_style)
        self.TW_logo_image.configure(self.root_style, image=image)
        self.TW_logo_image.image = image

        # 위치
        self.exit_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.LabelV.pack(fill=tk.BOTH, expand=True)
        self.video_label_1.pack(fill=tk.BOTH, expand=True)
        self.LabelV2.pack(fill=tk.BOTH, expand=True)
        self.video_label_2.pack(fill=tk.BOTH, expand=True)
        self.text_label.pack(fill=tk.BOTH, expand=True)
        self.TW_logo_image.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.button_image = None
        self.unit_name = "empty"
        self.mvapp = mvapp
        self.IC = ImageCV()

    def exit_clicked(self) -> None:
        # "X" 버튼이 클릭될 때 실행되는 함수로, 사용자에게 프로그램 종료를 확인하는 메시지 박스를 띄웁니다.
        result = messagebox.askquestion("Exit Confirmation", "프로그램을 종료 하시겠습니까?")
        if result == "yes":
            self.mvapp.exit()
            # 현재 프로세스 ID를 얻어 종료
            os.kill(os.getpid(), signal.SIGTERM)

    def video_label_update(self, image: np.ndarray, video_label) -> None:
        # 비디오 레이블을 업데이트하는 함수로, 주어진 이미지를 표시합니다.
        image = self.IC.image_tk(image)
        self.image = image
        video_label.configure(image=image)
        video_label.image = image
        self.photo_path_or = ""
        self.photo_path_sc = ""