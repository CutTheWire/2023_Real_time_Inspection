import cv2
import numpy as np
import os
import base64
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class CustomMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = ImageProcessor()

        # 이미지 디렉토리 선택 버튼
        select_dir_button = QPushButton('이미지 디렉토리 선택', self)
        select_dir_button.clicked.connect(self.open_img_dir_dialog)
        select_dir_button.move(20, 20)
        select_dir_button.setFixedWidth(200)  # 버튼의 너비를 200으로 설정

        # 이미지 처리 및 저장 버튼
        process_save_button = QPushButton('이미지 처리 및 저장', self)
        process_save_button.clicked.connect(self.process_and_save)
        process_save_button.move(20, 60)
        process_save_button.setFixedWidth(200)  # 버튼의 너비를 200으로 설정

        # aavg_img 레이블
        self.aavg_label = QLabel(self)
        self.aavg_label.setGeometry(250, 20, 200, 200)  # 레이블의 위치와 크기 설정

        # avg_img 레이블
        self.avg_label = QLabel(self)
        self.avg_label.setGeometry(500, 20, 200, 200)  # 레이블의 위치와 크기 설정

        # 실행 버튼
        execute_button = QPushButton('실행', self)
        execute_button.clicked.connect(self.process_and_save)
        execute_button.move(20, 100)
        execute_button.setFixedWidth(200)  # 버튼의 너비를 200으로 설정
        
        # 창 크기 고정
        self.setFixedSize(730, 250)

    def open_img_dir_dialog(self):
        self.processor.select_img_dir()

    def process_and_save(self):
        if self.processor.img_files is None:
            return
        save_dir = os.path.expanduser("~/Documents/TW")
        file_name = "avg_img"
        try:
            aavg_img, avg_img, mask = self.processor.process_images()
        except:
            return

        self.processor.save_avg_image(save_dir, file_name, avg_img)
        
        self.video_label_update(aavg_img, self.aavg_label)
        self.video_label_update(avg_img, self.avg_label)

    def video_label_update(self, image: np.ndarray, video_label: QLabel):
        '''
        이미지 업데이트, 레이블 크기에 맞게 이미지 스케일 조정 후
        레이블에 이미지 설정
        '''
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        h, w, c = image.shape
        qimg = QImage(image.data, w, h, w*c, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        if pixmap.width() > pixmap.height():  # If width is greater than height
            pixmap = pixmap.scaledToWidth(video_label.width())  # Scale pixmap to width of label
        else:
            pixmap = pixmap.scaledToHeight(video_label.height())  # Scale pixmap to height of label

        video_label.setPixmap(pixmap)

class ImageProcessor:
    def __init__(self):
        self.img_dir = None
        self.img_files = None
        self.first_img = None
        self.height = None
        self.width = None
        self.pixel_sum = None

        # 추가 코드: self.width와 self.height 초기화
        self.width = 0
        self.height = 0

    def select_img_dir(self):
        self.img_dir = QFileDialog.getExistingDirectory(window, "이미지 디렉토리 선택")
        if self.img_dir:
            self.img_files = [f for f in os.listdir(self.img_dir) if os.path.isfile(os.path.join(self.img_dir, f))]
            if not self.img_files:
                QMessageBox.warning(window, "경고", "선택한 디렉토리에 이미지 파일이 없습니다.")
                return
            

            self.first_img = cv2.imread(os.path.join(self.img_dir, self.img_files[0]), cv2.IMREAD_GRAYSCALE)
            if self.first_img is None:
                print("이미지를 불러올 수 없습니다.")
                return
            self.height, self.width = self.first_img.shape
            self.pixel_sum = np.zeros((self.height, self.width), np.float32)

                
    def process_images(self):
        for img_file in self.img_files:
            try:
                img = cv2.imread(os.path.join(self.img_dir, img_file), cv2.IMREAD_GRAYSCALE)
                img_resized = cv2.resize(img, (self.width, self.height))
                self.pixel_sum += img_resized
            except:
                return

        avg_img = (self.pixel_sum / len(self.img_files)).astype(np.uint8)
        _, aavg_img = cv2.threshold(avg_img, 80, 255, cv2.THRESH_TOZERO)
        _, mask = cv2.threshold(avg_img, 80, 255, cv2.THRESH_BINARY_INV)
        return aavg_img, avg_img, mask

    def save_avg_image(self, save_dir, file_name, avg_img):
        os.makedirs(save_dir, exist_ok=True)
        i = 1
        while os.path.exists(os.path.join(save_dir, f"{file_name}_{i}.ini")):
            i += 1
        _, buffer = cv2.imencode('.png', avg_img)
        img_base64 = base64.b64encode(buffer)
        with open(os.path.join(save_dir, f"{file_name}_{i}.ini"), 'w') as configfile:
            configfile.write(img_base64.decode())

app = QApplication([])
window = CustomMainWindow()
window.show()
app.exec_()
