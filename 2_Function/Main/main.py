import os
import cv2
import sys
import numpy as np
import signal
import copy
import time
import fasteners
from screeninfo import get_monitors
from typing import Tuple, Union
# from multiprocessing import Pool
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

class main(MainView):
    def __init__(self) -> None:
        super().__init__()
        # self.p = Pool(processes=1)
        self.ob = object_get()
        self.SV = save("NUT")
        self.Ar = Ardu()
        self.cam = Camera()
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)

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
    
    def keyPressEvent(self, event):
        '''
        ESC 키가 눌렸을 때
        플래그를 False로 설정하여 while문과 창을 종료합니다.
        '''
        if event.key() == Qt.Key_Escape:
            self.run = False
            lock.release()
            self.close()
            sys.exit()
            s
    def ssim_process(self, framea: np.ndarray) -> Tuple[int, float, np.ndarray]:
        '''
        ssim_process 함수는 이미지의 SSIM(Structural Similarity Index)를 계산
        이 함수에서는 framea 이미지를 받아서 적절한 크기로 조정하고
        이를 Mask 메소드를 사용하여 처리한 후에, DD(detect_defects) 함수를 호출합니다.
        '''
        mask = self.IC.Mask(framea, 80)
        # result = self.p.apply_async(DD, args=(mask,))
        # defects_num, ssim_value = result.get()
        defects_num, ssim_value = DD(mask)

        size = self.IC.Scale_Resolution(framea, 2)
        framea = cv2.resize(framea, size)
        return defects_num, ssim_value, framea, mask
    
    def list_output(self, defects_num: int, ssim_value: float) -> str:
        if defects_num == 1:
            self.text_label.setText(f"정상\n{round(ssim_value,2)}")
            self.text_label.setStyleSheet("background-color: #FFFFFF; color: #35B558; font-size: 75pt; border-radius: 10px;")
            self.text_label.setAlignment(Qt.AlignCenter)  # Add this line
            defects_name = "O"
        elif defects_num == 0:
            self.text_label.setText(f"불량\n{round(ssim_value,2)}")
            self.text_label.setStyleSheet("background-color: #FFFFFF; color: #B43437; font-size: 75pt; border-radius: 10px;")
            self.text_label.setAlignment(Qt.AlignCenter)  # This line is already here
            defects_name = "X"
        else:
            self.text_label.setText(f"확인 필요\n{round(ssim_value,2)}")
            self.text_label.setStyleSheet("background-color: #FFFFFF; color: #C7C53A; font-size: 75pt; border-radius: 10px;")
            self.text_label.setAlignment(Qt.AlignCenter)  # Add this line
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
        frame = self.IC.gray(frame)
        width, height = self.IC.Scale_Resolution(frame, 1)
        frame = cv2.resize(frame, (width, height))
        framea = copy.deepcopy(frame)
        framea= self.IC.gray(framea)
        try:
            frame, num, edit_image, binary = self.ob.get(frame, width, height, self.num_max, self.num_min)
        except:
            num = 0
        self.video_label_update(frame, self.video_label_1)

        if num != 0:
            defects_num, ssim_value, framea, mask = self.ssim_process(edit_image)
            # self.Ar.move(defects_num)
            self.video_label_update(edit_image, self.video_label_2)
            defects_name = self.list_output(defects_num, ssim_value)

            # self.SV.nut_image_save(framea, defects_name, ssim_value)
            self.SV.nut_image_save(mask, defects_name, ssim_value)
            self.SV.nut_image_save(edit_image, "image", ssim_value)

if __name__ == "__main__":
    # 락을 생성합니다.
    lock = fasteners.InterProcessLock('/tmp/my_lock_file')
    acquired = lock.acquire(blocking=False)

    if not acquired:
        # 락을 획득하지 못했으면 프로그램을 종료합니다.
        sys.exit()

    try:
        loading_screen = LoadingScreen()
        loading_screen.show()

        M = main()
        app = QApplication(sys.argv)
        M.check(loading_screen)
        # M.Ar_check(loading_screen)
        M.cam.open_camera()
        M.start()
        M.show()
        loading_screen.close()

        while M.run:
            try:
                M.updata_frame()
                time.sleep(0.05)
            except:
                pass
            QApplication.processEvents()

        
    finally:
        # 프로그램 종료 전에 락을 반드시 해제합니다.
        if acquired:
            lock.release()
            os.kill(os.getpid(), signal.SIGTERM)
            # M.p.close()
            # M.p.join()