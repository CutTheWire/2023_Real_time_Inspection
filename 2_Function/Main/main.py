import os
import cv2
import sys
import numpy as np
import signal
import copy
from screeninfo import get_monitors
from typing import Tuple, Union
from multiprocessing import Pool
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from IMG.IPP import ImageCV, save, object_get
from IMG.camera import Camera
from IMG.cv_grab_callback import App
from IMG.SSIM import detect_defects as DD

from TW.Loading import LoadingScreen
from TW.micro_servo import Ardu
from TW.TWSM import TW
from TW.UI import MainView

class main:
    def __init__(self) -> None:
        self.p = Pool(processes=2)
        self.IC = ImageCV()
        self.ob = object_get()
        self.SV = save("NUT")
        self.Ar = Ardu()
        self.cam = Camera()
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.end = True

    def Ar_check(self, loading_screen):
        if self.Ar.check():
            pass
        else:
            loading_screen.close()
            self.msg.setWindowTitle("HW ERROR")
            self.msg.setText('''현재 PC와 보드의 연결이 실패하였습니다.
                            \n케이블 연결을 확인하여 분리되어 있다면 결합해주세요.
                            \n연결 후 같은 메시지가 생성 된 경우 업체에 문의하시길 바랍니다.''')
            retval = self.msg.exec_()
            if retval == QMessageBox.Ok:
                os.kill(os.getpid(), signal.SIGTERM)

    def check(self, loading_screen) -> bool:
        # 초기화 함수에서는 필요한 객체와 변수를 초기화합니다.
        # 예를 들어, ImageCV 클래스의 인스턴스, object_get 클래스의 인스턴스, save 클래스의 인스턴스, Ardu 클래스의 인스턴스 등을 생성합니다.
        T = TW()
        if T() == True:
            pass
        else:
            loading_screen.close()
            if T() == False:
                self.msg.setWindowTitle("SM ERROR")
                self.msg.setText('''해당 프로그램은 등록 된 PC에서 실행 가능합니다.
                                \n변경을 원할 경우 업체에 요청하시길 바랍니다.''')
                retval = self.msg.exec_()
                if retval == QMessageBox.Ok:
                    os.kill(os.getpid(), signal.SIGTERM)
            elif T() == 2:
                self.msg.setWindowTitle("OS ERROR")
                self.msg.setText("해당 프로그램은 Windows10 이상에서만 실행 가능합니다.")
                retval = self.msg.exec_()
                if retval == QMessageBox.Ok:
                    os.kill(os.getpid(), signal.SIGTERM)
            else:
                self.msg.setWindowTitle("ERROR")
                self.msg.setText(str(T()))
                retval = self.msg.exec_()
                if retval == QMessageBox.Ok:
                    os.kill(os.getpid(), signal.SIGTERM)

    def image_thread(self, frame: np.ndarray, width, height,) -> Tuple[np.ndarray, np.ndarray, Union[int,tuple]]:
        result = self.p.apply_async(self.ob.get, args=(frame, width, height, 80))
        frame, num  = result.get()
        return frame, num

    def ssim_process(self, framea: np.ndarray, num: int) -> Tuple[int, float, np.ndarray]:
        '''
        ssim_process 함수는 이미지의 SSIM(Structural Similarity Index)를 계산
        이 함수에서는 framea 이미지를 받아서 적절한 크기로 조정하고
        이를 Mask 메소드를 사용하여 처리한 후에, DD(detect_defects) 함수를 호출합니다.
        '''
        framea = self.IC.edit(framea, num)
        mask = self.IC.Mask(framea, 80)
        result = self.p.apply_async(DD, args=(mask,))
        defects_num, ssim_value = result.get()

        size = self.IC.Scale_Resolution(framea, 2)
        framea = cv2.resize(framea, size)
        return defects_num, ssim_value, framea
    
    def list_output(self, defects_num: int, ssim_value: float) -> str:
        if defects_num == 1:
            MV.text_label.setText(f"정상")
            MV.text_label.setStyleSheet("background-color: #FFFFFF; color: #35B558; font-size: 75pt; border-radius: 10px;")
            MV.text_label.setAlignment(Qt.AlignCenter)  # Add this line
            defects_name = "O"
        elif defects_num == 0:
            MV.text_label.setText(f"불량")
            MV.text_label.setStyleSheet("background-color: #FFFFFF; color: #B43437; font-size: 75pt; border-radius: 10px;")
            MV.text_label.setAlignment(Qt.AlignCenter)  # This line is already here
            defects_name = "X"
        else:
            MV.text_label.setText(f"확인 필요")
            MV.text_label.setStyleSheet("background-color: #FFFFFF; color: #C7C53A; font-size: 75pt; border-radius: 10px;")
            MV.text_label.setAlignment(Qt.AlignCenter)  # Add this line
            defects_name = "X"
        return defects_name


    def start(self) -> None:
        self.mvapp = App()
        self.mvapp.main()
        monitors = get_monitors()
        screen_width = monitors[0].width
        self.cam.set_cap_size(screen_width, (screen_width*9)//16)

    def cam_check(self) -> np.ndarray:
        if self.mvapp.frame is not None:
            return self.mvapp.frame
        else:
            return M.cam.get_frame()

    def updata_frame(self):
        frame = self.cam_check()
        width, height = self.IC.Scale_Resolution(frame, 0.6)
        frame = cv2.resize(frame, (width, height))
        framea = copy.deepcopy(frame)
        framea= self.IC.gray(framea)
        try:
            frame, num = self.image_thread(frame, width, height)
        except:
            num = 0
        MV.video_label_update(frame, MV.video_label_1)

        if num != 0:
            defects_num, ssim_value, framea = self.ssim_process(framea, num)
            # self.Ar.move(defects_num)
            MV.video_label_update(framea, MV.video_label_2)
            defects_name = self.list_output(defects_num, ssim_value)
            self.SV.nut_image_save(framea, defects_name, ssim_value)



if __name__ == "__main__":
    loading_screen = LoadingScreen()
    loading_screen.show()
    
    M = main()
    app = QApplication(sys.argv)
    M.check(loading_screen)
    M.Ar_check(loading_screen)
    MV = MainView(M.p)
    M.cam.open_camera()
    M.start()
    MV.show()
    loading_screen.close()
    while MV.run:
        M.updata_frame()
        QApplication.processEvents()