import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

class CameraDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("카메라 영상")
        
        self.video_capture = cv2.VideoCapture(0)  # 카메라를 열기
        
        # 해상도 설정 (2K)
        self.video_capture.set(3, 1920)  # 가로 해상도
        self.video_capture.set(4, 1080)  # 세로 해상도
        self.video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # 코덱 설정 (예: MJPEG)
        self.video_capture.set(cv2.CAP_PROP_BITRATE, 10000)
        
        layout = QVBoxLayout()
        self.label = QLabel(self)
        layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignCenter)
        
        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  # 30ms마다 프레임 업데이트
        
    def update_frame(self):
        ret, frame = self.video_capture.read()
        
        if ret:
            # OpenCV BGR 이미지를 RGB 이미지로 변환
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Numpy 배열을 QImage로 변환
            q_image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            
            # QLabel에 이미지 표시
            self.label.setPixmap(QPixmap.fromImage(q_image))
        
    def closeEvent(self, event):
        self.video_capture.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraDisplay()
    window.show()
    sys.exit(app.exec_())
