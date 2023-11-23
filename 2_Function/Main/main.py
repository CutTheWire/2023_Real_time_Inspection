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
        # 초기화 함수에서는 필요한 객체와 변수를 초기화합니다.
        # 예를 들어, ImageCV 클래스의 인스턴스, object_get 클래스의 인스턴스, save 클래스의 인스턴스, Ardu 클래스의 인스턴스 등을 생성합니다.
        self.p = Pool(processes=2)
        self.IC = ImageCV()
        self.ob = object_get()
        self.SV = save("NUT")
        self.Ar = Ardu()
        self.end = True

    def check(self) -> bool:
        # 초기화 함수에서는 필요한 객체와 변수를 초기화합니다. 
        # 예를 들어, ImageCV 클래스의 인스턴스, object_get 클래스의 인스턴스, save 클래스의 인스턴스, Ardu 클래스의 인스턴스 등을 생성합니다.
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
        # image_thread 함수는 이미지 프로세싱 작업을 수행합니다. 멀티프로세싱을 사용하여 병렬 처리를 합니다.
        # 이 함수에서는 프레임을 받아서 적절한 크기로 조정하고, 이를 복사한 후에 object_get 클래스의 get 메소드를 호출하여 처리합니다.
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        width, height = self.IC.Scale_Resolution(frame, 0.6)
        frame = cv2.resize(frame, (width, height))
        framea = copy.deepcopy(frame)
        result = self.p.apply_async(self.ob.get, args=(frame, width, height))
        frame, num  = result.get()
        return frame, framea, num

    def ssim_process(self, framea: np.ndarray, num: int) -> Tuple[int, float, np.ndarray]:
        # ssim_process 함수는 이미지의 SSIM(Structural Similarity Index)를 계산하고, 이를 기반으로 이미지를 처리하는 역할을 합니다.
        # 이 함수에서는 framea 이미지를 받아서 적절한 크기로 조정하고, 이를 Mask 메소드를 사용하여 처리한 후에, DD(detect_defects) 함수를 호출합니다.
        framea = self.IC.edit(framea, num)
        mask = self.IC.Mask(framea, 85)
        result = self.p.apply_async(DD, args=(mask,))
        defects_num, ssim_value = result.get()
        size = self.IC.Scale_Resolution(framea, 2)
        framea = cv2.resize(framea, size)
        return defects_num, ssim_value, framea

    def start(self, loading_screen):
        # start 함수는 애플리케이션을 시작하는 역할을 합니다. 
        # tkinter를 이용하여 GUI를 설정하고, 메인 루프를 실행합니다. 
        # 이 함수에서는 먼저 로딩 화면을 닫고, 메인 윈도우를 생성하고, 이를 기반으로 MainView 클래스의 인스턴스를 생성합니다. 
        # 그리고 비디오 프레임을 받아서 image_thread 함수와 ssim_process 함수를 호출하여 처리하고, 그 결과를 GUI에 표시합니다.
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
                    # SV.nut_image_save(framea, defects_name, ssim_value) # 이미지 저장용
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