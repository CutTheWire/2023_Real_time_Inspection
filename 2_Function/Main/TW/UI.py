from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, QTextEdit, QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import configparser
import os
import base64

from IMG.IPP import ImageCV
import DATA.base64_data as B64D

class MainView(QWidget):
    def __init__(self):
        super().__init__()
                # 추가: configparser 객체 생성 및 파일 경로 설정
        self.config = configparser.ConfigParser()
        self.ini_file_path = os.path.expanduser("~\\Documents\\TW\\config.ini")
        self.load_config()
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

    def load_config(self):
        '''ini 파일이 존재하면 설정을 불러오고, 없으면 기본값 설정'''
        if os.path.exists(self.ini_file_path):
            self.config.read(self.ini_file_path)
            self.num_min = self.config.getint('Settings', 'num_min')
            self.num_max = self.config.getint('Settings', 'num_max')
            self.unit_name = self.config.get('Settings', 'unit_name')
        else:
            self.num_min = 135
            self.num_max = 256
            self.unit_name = "empty" # 부품 이름을 지정하는 UI를 추가시 해당 변수 사용
        self.save_config()

    def save_config(self):
        '''설정을 ini 파일에 저장'''
        self.config['Settings'] = {'num_min': str(self.num_min), 'num_max': str(self.num_max), 'unit_name': self.unit_name}
        with open(self.ini_file_path, 'w') as configfile:
            self.config.write(configfile)

    def button_clicked(self):
        '''인식 범위를 지정하는 함수입니다.'''
        try:
            self.num_min = int(self.min_text_edit.text())
        except ValueError:
            self.num_min = 135
            self.min_text_edit.setText(str(self.num_min))
        try:
            self.num_max = int(self.max_text_edit.text())
        except ValueError:
            self.num_max = 256
            self.max_text_edit.setText(str(self.num_max))
        self.save_config()
        print(f"저장된 범위{self.num_min, self.num_max}")

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