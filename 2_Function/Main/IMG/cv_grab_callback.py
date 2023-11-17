#coding=utf-8
import numpy as np
import IMG.mvsdk as mvsdk
import platform
import copy
from typing import Any

class App(object):
    def __init__(self) -> None:
        self.pFrameBuffer = 0
        self._frame = None

    def main(self) -> str:
        # 카메라 열거
        DevList = mvsdk.CameraEnumerateDevice()
        nDev = len(DevList)
        if nDev < 1:
            return "카메라를 찾을 수 없습니다!"
            
        for i, DevInfo in enumerate(DevList):
            print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
        i = 0 if nDev == 1 else int(input("카메라 선택: "))
        DevInfo = DevList[i]

        # 카메라
        hCamera = 0
        self.hCamera = hCamera

        try:
            hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
        except mvsdk.CameraException as e:
            return f"카메라 초기화 실패 {e}"

        # 카메라 기능 확인
        cap = mvsdk.CameraGetCapability(hCamera)

        # 흑백 카메라인지, 컬러 카메라인지 확인
        monoCamera = (cap.sIspCapacity.bMonoSensor != 0)

        # 흑백 카메라인 경우, ISP가 24비트 그레이스케일로 확장하는 대신 MONO 데이터를 직접 출력하도록 함
        if monoCamera:
            mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

        # 카메라 모드를 연속 캡처로 변경
        mvsdk.CameraSetTriggerMode(hCamera, 0)

        # 수동 노출, 노출 시간 30ms로 설정
        mvsdk.CameraSetAeState(hCamera, 0)
        mvsdk.CameraSetExposureTime(hCamera, 10 * 1000)

        # SDK 내부 캡처 스레드를 시작하도록 함
        mvsdk.CameraPlay(hCamera)

        # RGB 버퍼의 크기 계산, 여기서는 카메라의 최대 해상도를 기준으로 할당
        FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)

        # RGB 버퍼 할당, ISP 출력 이미지를 저장하는 데 사용
        # 참고: 카메라에서 PC로 전송되는 것은 RAW 데이터이며, PC에서는 소프트웨어 ISP를 사용하여 RGB 데이터로 변환(흑백 카메라인 경우 형식을 변경할 필요가 없지만 ISP에는 다른 처리가 있으므로 이 버퍼가 필요함)
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)
        
        mvsdk.CameraSetCallbackFunction(hCamera, self.GrabCallback, 0)

    @mvsdk.method(mvsdk.CAMERA_SNAP_PROC)
    def GrabCallback(self, hCamera: Any, pRawData: Any, pFrameHead: Any, pContext: Any) -> None:
        FrameHead = pFrameHead[0]
        pFrameBuffer = self.pFrameBuffer
        try:
            mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
            mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)

            # Windows에서 얻은 이미지 데이터는 상하로 뒤집혀 있고 BMP 형식으로 저장됨. OpenCV로 변환하기 위해 올바르게 상하로 뒤집어야 함
            # Linux에서는 이미지가 직접 출력되며 상하로 뒤집을 필요가 없음
            if platform.system() == "Windows":
                mvsdk.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)

            # 이제 이미지는 pFrameBuffer에 저장되며, 컬러 카메라의 경우 pFrameBuffer = RGB 데이터, 흑백 카메라의 경우 pFrameBuffer = 8비트 그레이스케일 데이터임
            # pFrameBuffer를 OpenCV 이미지 형식으로 변환하여 후속 알고리즘 처리 수행
            frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3) )
            self.frame = copy.deepcopy(frame)
        except:
            pass

    @property
    def frame(self) -> np.ndarray:
        return self._frame
    
    @frame.setter
    def frame(self, frame: np.ndarray):
        self._frame = frame

    def exit(self) -> None:
        # 카메라 종료
        mvsdk.CameraUnInit(self.hCamera)
        # 프레임 버퍼 해제
        mvsdk.CameraAlignFree(self.pFrameBuffer)

