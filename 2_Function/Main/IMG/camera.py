import cv2
import numpy as np
from pygrabber.dshow_graph import FilterGraph

class Camera:
    def __init__(self) -> None:
        """
        Camera 클래스의 초기화 함수입니다. 사용 가능한 카메라, 장치 등을 초기 설정합니다.
        """
        self.available_cameras = {}
        self.devices = FilterGraph().get_input_devices()
        self.camera_name = 'HD 4MP WEBCAM'
        self.cap = None
        self.name = ""
        
    def get_available_cameras(self) -> None:
        """
        사용 가능한 카메라를 가져오는 함수입니다.
        """
        self.available_cameras = {}
        for device_index, device_name in enumerate(self.devices):
            self.available_cameras[device_index] = device_name
    
    def cameras_list(self) -> list:
        """
        사용 가능한 카메라의 목록을 반환하는 함수입니다.
        """
        self.get_available_cameras()
        return self.available_cameras
    
    def open_camera(self) -> tuple:
        """
        카메라를 열고, 카메라 이름을 설정하는 함수입니다.
        """
        available_cameras = self.cameras_list()
        for i in available_cameras:
            if available_cameras[i] == self.camera_name:
                self.cap = cv2.VideoCapture(i)
                self.name = available_cameras[i]
            elif self.cap == None:
                self.cap = cv2.VideoCapture(0)
                self.name = available_cameras[0]
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', 'E', 'V', 'C'))
        return self.cap
    
    def set_cap_size(self, width: int, height: int) -> None:
        """
        카메라의 캡처 크기를 설정하는 함수입니다.
        """
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)

    def get_frame(self) -> np.ndarray:
        """
        카메라에서 프레임을 가져오는 함수입니다.
        """
        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
        except:
            # 오류가 발생한 경우 검은 화면 이미지 출력
            black_frame = np.zeros((int(self.cap.get(4)), int(self.cap.get(3)), 3), dtype=np.uint8)
            return black_frame
                

    def release_camera(self) -> None:
        """
        카메라를 해제하는 함수입니다.
        """
        if self.cap is not None:
            self.cap.release()

    def is_camera_open(self) -> bool:
        """
        카메라가 열려 있는지 확인하는 함수입니다.
        """
        return self.cap is not None

    def __del__(self) -> None:
        """
        Camera 객체가 소멸될 때 카메라를 해제하는 함수입니다.
        """
        self.release_camera()
