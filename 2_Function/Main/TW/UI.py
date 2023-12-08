from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import sys
import cv2
import numpy as np
import base64

from IMG.IPP import ImageCV
import DATA.base64_data as B64D

class MainView(QWidget):
    def __init__(self, p):
        super().__init__()
        
        # 스타일 설정
        self.label_style = "background-color: #FFFFFF; border-radius: 10px;"
        self.back_style = "background-color: #F5F5F7;"

        # GUI 생성
        self.video_label_1 = QLabel(self)
        self.video_label_2 = QLabel(self)
        self.text_label = QLabel("ㅤㅤ", self)
        self.TW_logo_image = QLabel(self)

        # 스타일 적용
        self.video_label_1.setStyleSheet(self.label_style)
        self.video_label_2.setStyleSheet(self.label_style)
        self.text_label.setStyleSheet(self.label_style)
        self.video_label_1.setAlignment(Qt.AlignCenter)
        self.video_label_2.setAlignment(Qt.AlignCenter)
        self.text_label.setAlignment(Qt.AlignCenter)


        # 이미지 설정
        pixmap = QPixmap()
        self.image_data = base64.b64decode(B64D.logo_image_base64)
        pixmap.loadFromData(self.image_data, "PNG")
        self.TW_logo_image.setPixmap(pixmap)

        '''
        수평 박스 레이아웃 생성
        위젯을 오른쪽으로 밀어낼 공백 아이템 추가
        위젯을 레이아웃에 추가
        '''
        hbox = QHBoxLayout()
        hbox.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        hbox.addWidget(self.TW_logo_image)

        # 레이아웃 설정
        grid = QGridLayout()
        grid.addWidget(self.video_label_1,  0, 0, 10, 2)
        grid.addWidget(self.video_label_2, 0, 2, 5, 1)
        grid.addWidget(self.text_label,5, 2, 5, 1)
        grid.addLayout(hbox, 10, 0, 1, 3)  # 이 부분을 조정함
        self.setLayout(grid)

        self.unit_name = "empty"
        self.IC = ImageCV()
        self.run = True
        self.p = p
        
    def show(self) -> None:
        '''로딩 화면을 전체 화면으로 표시하는 함수입니다.'''
        super().showFullScreen()

    def close(self) -> None:
        '''로딩 창을 닫는 함수입니다.'''
        super().close()

    def is_cv2_image(self, image):
        return isinstance(image, np.ndarray)

    def  video_label_update(self, image: np.ndarray, video_label: QLabel):
        '''
        이미지 업데이트, 레이블 크기에 맞게 이미지 스케일 조정 없이
        레이블에 이미지 설정
        '''
        if self.is_cv2_image(image):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            h, w, c = image.shape
            qimg = QImage(image.data, w, h, w*c, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(image, "PNG")

        if pixmap.width() > pixmap.height():  # If width is greater than height
            pixmap = pixmap.scaledToWidth(video_label.width())  # Scale pixmap to width of label
        else:
            pixmap = pixmap.scaledToHeight(video_label.height())  # Scale pixmap to height of label

        video_label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        '''
        ESC 키가 눌렸을 때
        플래그를 False로 설정하여 while문과 창을 종료합니다.
        '''
        if event.key() == Qt.Key_Escape:
            self.run = False
            self.p.close()
            self.p.join()
            self.close()
            sys.exit()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     mv = MainView()
#     while mv.run:
#         mv.show()
#         mv.video_label_update(mv.image_data, mv.video_label_1)
#         QApplication.processEvents()  # 이 함수를 호출하여 이벤트 루프를 유지합니다.