from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, QTextEdit, QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import fasteners
import base64

from IMG.IPP import ImageCV
import DATA.base64_data as B64D

class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.num_min =70 
        self.num_max = 150
        self.unit_name = "empty"
        self.IC = ImageCV()
        self.run = True

        # 스타일 설정
        self.label_style = "background-color: #FFFFFF; color: #000000; font-size: 25pt; border-radius: 10px"
        self.edit_style = "background-color: #DFDFDF; color: #000000; font-size: 25pt; border-radius: 10px"
        self.button_style = "background-color: #BDBDBF; color: #000000; font-size: 25pt; border-radius: 10px"
        self.back_style = "background-color: #F5F5F7;"

        # GUI 생성
        self.video_label_1 = QLabel(self)
        self.video_label_2 = QLabel(self)
        self.text_label = QLabel("ㅤㅤ", self)
        self.TW_logo_image = QLabel(self)
        self.min_text_label = QLabel("MIN", self)
        self.min_text_edit = QLineEdit(str(self.num_min), self)
        self.max_text_label = QLabel("MAX", self)
        self.max_text_edit = QLineEdit(str(self.num_max),self)
        self.apply_button = QPushButton('&APPLY', self)

        # 스타일 적용
        self.video_label_1.setStyleSheet(self.label_style)
        self.video_label_2.setStyleSheet(self.label_style)
        self.text_label.setStyleSheet(self.label_style)
        self.min_text_label.setStyleSheet(self.label_style)
        self.min_text_edit.setStyleSheet(self.edit_style)
        self.max_text_label.setStyleSheet(self.label_style)
        self.max_text_edit.setStyleSheet(self.edit_style)
        self.apply_button.setStyleSheet(self.button_style)

        self.video_label_1.setAlignment(Qt.AlignCenter)
        self.video_label_2.setAlignment(Qt.AlignCenter)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.min_text_label.setAlignment(Qt.AlignCenter)
        self.min_text_edit.setAlignment(Qt.AlignCenter)
        self.max_text_label.setAlignment(Qt.AlignCenter)
        self.max_text_edit.setAlignment(Qt.AlignCenter)

        self.min_text_edit.setFixedHeight(50)
        self.max_text_edit.setFixedHeight(50)
        self.apply_button.setFixedHeight(50)
        self.apply_button.setCheckable(True)
        self.apply_button.toggle()
        self.apply_button.clicked.connect(self.button_clicked)

        min_validator = QIntValidator(0, 254, self)
        max_validator = QIntValidator(1, 255, self)

        self.min_text_edit.setValidator(min_validator)
        self.max_text_edit.setValidator(max_validator)

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
        grid.addWidget(self.video_label_1,  0, 0, 10, 6)
        grid.addWidget(self.video_label_2, 0, 6, 5, 4)
        grid.addWidget(self.text_label, 5, 6, 5, 4)
        grid.addWidget(self.min_text_label, 10, 0, 1, 1)
        grid.addWidget(self.min_text_edit, 10, 1, 1, 3)
        grid.addWidget(self.max_text_label, 10, 4, 1, 1)
        grid.addWidget(self.max_text_edit, 10, 5, 1, 3)
        grid.addWidget(self.apply_button, 10, 8, 1, 2)
        grid.addLayout(hbox, 11, 0, 1, 10)
        self.setLayout(grid)

    def button_clicked(self):
        try:
            self.num_min = int(self.min_text_edit.text())
        except ValueError:
            self.num_min = 80
            self.min_text_edit.setText(str(self.num_min))
        try:
            self.num_max = int(self.max_text_edit.text())
        except ValueError:
            self.num_max = 120
            self.max_text_edit.setText(str(self.num_max))

        # min 값이 max 값보다 클 경우, min을 (max - 1)로 설정
        # max 값이 min 값보다 작을 경우, max를 (min + 1)로 설정
        if self.num_min > self.num_max:
            self.num_min = self.num_max - 1
            self.min_text_edit.setText(str(self.num_min))
        elif self.num_max < self.num_min:
            self.num_max = self.num_min + 1
            self.max_text_edit.setText(str(self.num_max))

        print(self.num_min, self.num_max)

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

        # Scale pixmap to fit inside the label, maintaining aspect ratio
        pixmap = pixmap.scaled(video_label.width(), video_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        video_label.setPixmap(pixmap)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     mv = MainView()
#     while mv.run:
#         mv.show()
#         mv.video_label_update(mv.image_data, mv.video_label_1)
#         QApplication.processEvents()  # 이 함수를 호출하여 이벤트 루프를 유지합니다.