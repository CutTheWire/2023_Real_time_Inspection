from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QIcon, QImage, QPixmap
import base64_icon as B
import cv2
import base64
import os
import glob

class CustomMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = ImageProcessor()

        select_file_button = QPushButton('이미지 파일 선택', self)
        select_file_button.clicked.connect(self.processor.select_img_file)
        select_file_button.move(20, 20)
        select_file_button.setFixedWidth(200)

        # 이미지 저장 버튼
        save_button = QPushButton('이미지 저장', self)
        save_button.clicked.connect(self.processor.save_img_as_base64)
        save_button.move(20, 60)
        save_button.setFixedWidth(200)

        # 이미지 레이블
        self.img_label = QLabel(self)
        self.img_label.setGeometry(250, 20, 200, 200)

        # 저장 상태 레이블
        self.status_label = QLabel(self)
        self.status_label.setGeometry(20, 100, 200, 150)

        self.setFixedSize(500, 300)
        self.setWindowTitle("Image To Base64")
        self.setWindowIcon(self.Icon())


    def update_img_label(self, img_file):
        img = cv2.imread(img_file)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        qimg = QImage(img.data, w, h, w * c, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        if pixmap.width() > pixmap.height():
            pixmap = pixmap.scaledToWidth(self.img_label.width())
        else:
            pixmap = pixmap.scaledToHeight(self.img_label.height())

        self.img_label.setPixmap(pixmap)

    def Icon(self):
        # QByteArray 객체 생성
        data = QByteArray.fromBase64(B.base64_icon.encode())  # 문자열을 바이트 문자열로 인코딩

        # QBuffer 객체 생성
        buffer = QBuffer(data)
        buffer.open(QIODevice.ReadOnly)

        # QPixmap 객체 생성
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.data())

        # QIcon 객체 생성
        icon = QIcon(pixmap)
        return icon


    def update_status_label(self, ini_file_count, last_saved_file, selected_file, save_status):
        self.status_label.setText(f"ini 파일 수: {ini_file_count}\n"
                                f"최근 저장된 파일: {last_saved_file}\n"
                                f"선택된 파일 이름: {selected_file}\n"
                                f"선택된 파일 저장 상태: {save_status}")

class ImageProcessor:
    def __init__(self):
        self.img_file = None

    def select_img_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.img_file, _ = QFileDialog.getOpenFileName(window, "이미지 파일 선택", "",
                                                       "Images (*.png *.jpg *.jpeg)", options=options)
        if self.img_file:
            window.update_img_label(self.img_file)
            window.update_status_label(self.get_ini_file_count(), "N/A", self.img_file, "NOT SAVE")

    def save_img_as_base64(self):
        if self.img_file is None:
            return
        img = cv2.imread(self.img_file)
        _, buffer = cv2.imencode('.png', img)
        img_base64 = base64.b64encode(buffer)
        save_dir = os.path.expanduser("~/Documents/TW")
        os.makedirs(save_dir, exist_ok=True)
        base_name = os.path.basename(self.img_file)
        file_name, _ = os.path.splitext(base_name)
        save_path = os.path.join(save_dir, f"{file_name}.ini")
        with open(save_path, 'w') as configfile:
            configfile.write(img_base64.decode())
        window.update_status_label(self.get_ini_file_count(), save_path, self.img_file, "SAVE")

    def get_ini_file_count(self):
        save_dir = os.path.expanduser("~/Documents/TW")
        ini_files = glob.glob(os.path.join(save_dir, "*.ini"))
        return len(ini_files)

app = QApplication([])
window = CustomMainWindow()
window.update_status_label(ImageProcessor().get_ini_file_count(), "N/A", "N/A", "N/A")
window.show()
app.exec_()
