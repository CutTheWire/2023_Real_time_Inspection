import os
import sys
import cv2
import time
import numpy as np
import signal
import copy
import gc

import tkinter as tk
from tkinter import font
from tkinter import messagebox
from multiprocessing import Pool
import matplotlib
matplotlib.use("Qt5Agg")  # 원하는 백엔드로 변경
from screeninfo import get_monitors

from IMG.IPP import ImageCV
from IMG.cv_grab_callback import App
from IMG.Image_Save import save
from IMG.ob_get import object_get
from IMG.SSIM import detect_defects as DD

from TW.TWSM import TW
from TW.Loading import LoadingScreen

import DATA.base64_data as B64D

class MainView:
    def __init__(self, root, mvapp):
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
        self.video_label = tk.Label(self.LabelV)
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
        self.video_label.configure(self.back_style)
        self.video_label_2.configure(self.back_style)
        self.text_label.configure(self.text_label_style)
        self.TW_logo_image.configure(self.root_style, image=image)
        self.TW_logo_image.image = image

        # 위치
        self.exit_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.LabelV.pack(fill=tk.BOTH, expand=True)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        self.LabelV2.pack(fill=tk.BOTH, expand=True)
        self.video_label_2.pack(fill=tk.BOTH, expand=True)
        self.text_label.pack(fill=tk.BOTH, expand=True)
        self.TW_logo_image.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.button_image = None
        self.unit_name = "empty"
        self.mvapp = mvapp

    def exit_clicked(self):
        result = messagebox.askquestion("Exit Confirmation", "프로그램을 종료 하시겠습니까?")
        if result == "yes":
            end = False
            self.mvapp.exit()
            # 현재 프로세스 ID를 얻어 종료
            os.kill(os.getpid(), signal.SIGTERM)

    def video_label_update(self, image: np.ndarray):
        self.image = image
        self.video_label.configure(image=image)
        self.video_label.image = image
        self.photo_path_or = ""
        self.photo_path_sc = ""

    def video_label_2_update(self, image: np.ndarray):
        self.image = image
        self.video_label_2.configure(image=image)
        self.video_label_2.image = image
        self.photo_path_or = ""
        self.photo_path_sc = ""

IC = ImageCV()
ob = object_get()
SV = save("NUT", "SUA502M")

def process(framea, num):
    framea = IC.edit(framea, num)
    del num

    mask = IC.Mask(framea, 85)
    SV.nut_image_save(mask)
    defects_num, ssim_value = DD(mask)
    del mask

    size = IC.Scale_Resolution(framea, 2)
    framea = cv2.resize(framea, size)
    return defects_num, ssim_value, framea            

if __name__ == "__main__":
    T = TW()
    root = tk.Tk()
    root.withdraw()
    if T() == True:
        end = True

        loading_screen = LoadingScreen()
        loading_screen.show()
        mvapp = App()

        app = MainView(root, mvapp)
        loading_screen.close()
        root.deiconify()
        
        p = Pool(processes=2)

        n = mvapp.main()
        if type(n) == str:
            messagebox.showinfo("ERROR", n)
            sys.exit()
        else:
            pass
        del loading_screen

        while end:
            frame = mvapp.frame
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                width, height = IC.Scale_Resolution(frame, 0.6)
                frame = cv2.resize(frame, (width, height))
                framea = copy.deepcopy(frame)
                # result =  p.apply_async(process_get, args=((frame, width, height),))
                # frame, num = result.get()
                frame, num = ob.get(frame, width, height)
                try:
                    image_tk = IC.image_tk(frame)
                    app.video_label_update(image_tk)
                    root.update()
                except:
                    end = False
                    break
                del image_tk
                if num != 0: 
                    try:
                        result = p.apply_async(process, args=(framea, num))
                        defects_num, ssim_value, framea = result.get()
                        image_tk1 = IC.image_tk(framea)
                        app.video_label_2_update(image_tk1)
                    except:
                        end = False
                        break
                    del image_tk1  

                    if defects_num == 1:
                        app.text_label.config(text="정상", fg="#35B558")
                    elif defects_num == 0:
                        app.text_label.config(text=f"불량", fg="#B43437")
                    else:
                        app.text_label.config(text=f"확인 필요\n유사도 : {round(ssim_value, 2)}", fg="#C7C53A")
                    del ssim_value            
            time.sleep(0.01)
                
        root.mainloop()
        gc.collect()
        # 카메라 종료.
        p.close
        p.join
        try:
            root.destroy()
        except tk.TclError:
            pass
        os.kill(os.getpid(), signal.SIGTERM)

    elif T() == False:
        messagebox.showinfo("SM ERROR", "해당 프로그램은 설정된 컴퓨터에서 실행 가능합니다.\n변경을 원할 경우 업체에 요청하시길 바랍니다.")

    elif T() == 2:
        messagebox.showinfo("OS ERROR", "해당 프로그램은 Windows10 이상에서만 실행 가능합니다.")

    else:
        messagebox.showinfo("ERROR", T())