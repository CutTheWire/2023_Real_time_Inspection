import base64
from PyQt5.QtWidgets import QApplication, QWidget
app = QApplication([])
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QPoint
from screeninfo import get_monitors

import DATA.base64_data as logo

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" ")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.resize(650, 400)  # 창 크기 설정

        # 로딩 중 이미지를 표시할 QLabel
        self.loading_label = QLabel(self)

        # 로딩 이미지를 base64로 변경하여 QLabel에 설정
        base64_image = logo.logo_image_base64
        image_data = base64.b64decode(base64_image)
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        self.loading_label.setPixmap(pixmap)

        # 수직 레이아웃을 사용하여 이미지를 중앙에 배치
        layout = QVBoxLayout(self)
        layout.addWidget(self.loading_label)
        layout.setAlignment(Qt.AlignCenter)

        self.loading_label.setAutoFillBackground(False)  # 배경 채우기 비활성화
        self.loading_label.setAttribute(Qt.WA_TranslucentBackground)  # 배경을 투명하게 만듭니다

        # 중앙 좌표를 계산
        center_point = self.calculateCenterPoint()
        self.moveCenter(center_point)

    def calculateCenterPoint(self):
        monitors = get_monitors()
        x = 0
        y = 0
        if monitors:
            monitor = monitors[0]
            x += monitor.width
            y += monitor.height
            center_x = x // 2
            center_y = y // 2
            return QPoint(center_x, center_y)
        else:
            return QPoint(x, y)

    def moveCenter(self, point):
        qr = self.frameGeometry()
        qr.moveCenter(point)
        self.move(qr.topLeft())

    def show(self):
        super().show()

    def close(self):
        # 로딩 창을 닫음
        super().close()