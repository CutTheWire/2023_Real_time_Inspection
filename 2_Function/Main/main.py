import os
import cv2
import time
import numpy as np
import signal
import copy
import gc
from typing import Tuple, Union
from multiprocessing import Pool
import tkinter as tk
from tkinter import messagebox

from IMG.IPP import ImageCV, save, object_get
from IMG.cv_grab_callback import App
from IMG.SSIM import detect_defects as DD

from TW.Loading import LoadingScreen
from TW.micro_servo import Ardu
from TW.thread import NewThread
from TW.TWSM import TW
from TW.UI import MainView

class main:
    def __init__(self) -> None:
        self.p = Pool(processes=2)
        self.IC = ImageCV()
        self.ob = object_get()
        self.SV = save("NUT")
        self.Ar = Ardu()
        self.end = True

    def check(self) -> bool:
        T = TW()
        if T() == True:
            return True 
        elif T() == False:
            messagebox.showinfo("SM ERROR", "해당 프로그램은 설정된 컴퓨터에서 실행 가능합니다.\n변경을 원할 경우 업체에 요청하시길 바랍니다.")
        elif T() == 2:
            messagebox.showinfo("OS ERROR", "해당 프로그램은 Windows10 이상에서만 실행 가능합니다.")
        else:
            messagebox.showinfo("ERROR", T())

    def image_thread(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Union[int,tuple]]:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        width, height = self.IC.Scale_Resolution(frame, 0.6)
        frame = cv2.resize(frame, (width, height))
        framea = copy.deepcopy(frame)
        result = self.p.apply_async(self.ob.get, args=(frame, width, height))
        frame, num  = result.get()
        return frame, framea, num

    def ssim_process(self, framea: np.ndarray, num: int) -> Tuple[int, float, np.ndarray]:
        framea = self.IC.edit(framea, num)
        mask = self.IC.Mask(framea, 85)
        result = self.p.apply_async(DD, args=(mask,))
        defects_num, ssim_value = result.get()
        size = self.IC.Scale_Resolution(framea, 2)
        framea = cv2.resize(framea, size)
        return defects_num, ssim_value, framea

    def start(self, loading_screen):        
        root = tk.Tk()
        mvapp = App()
        app = MainView(root, mvapp)
        mvapp.main()
        
        loading_screen.close()
        del loading_screen
        gc.collect()

        while self.end:
            frame = mvapp.frame
            if frame is not None:
                thread_1 = NewThread(target=self.image_thread, args=(frame,))
                thread_1.start()
                frame, framea, num = thread_1.join()
                app.video_label_update(frame, app.video_label_1)    
                if num != 0: 
                    thread_2 = NewThread(target=self.ssim_process, args=(framea, num))
                    thread_2.start()
                    defects_num, ssim_value, framea = thread_2.join()
                    self.Ar.move(defects_num)
                    app.video_label_update(framea, app.video_label_2)
                    if defects_num == 1:
                        app.text_label.config(text="정상", fg="#35B558")
                        defects_name = "정상"
                    elif defects_num == 0:
                        app.text_label.config(text=f"불량", fg="#B43437")
                        defects_name = "불량"
                    else:
                        app.text_label.config(text=f"확인 필요 유사도 : {round(ssim_value, 2)}", fg="#C7C53A")
                        defects_name = "확인필요" 
                    # SV.nut_image_save(framea, defects_name, ssim_value)   
            root.update()
        root.mainloop()
        root.destroy()

if __name__ == "__main__":
    loading_screen = LoadingScreen()
    loading_screen.show()
    M = main()
    HW_result = M.check()
    if HW_result == True:
        M.start(loading_screen)
        M.end = False
        os.kill(os.getpid(), signal.SIGTERM)