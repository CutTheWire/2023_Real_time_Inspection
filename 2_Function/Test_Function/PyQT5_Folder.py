from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog

def open_file_dialog():
    file_path, _ = QFileDialog.getOpenFileName(window, '파일 선택')
    print('선택한 파일 경로:', file_path)

app = QApplication([])
window = QMainWindow()

button = QPushButton('파일 탐색기 열기', window)
button.clicked.connect(open_file_dialog)

window.show()
app.exec_()
