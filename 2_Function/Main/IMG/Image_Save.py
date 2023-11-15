import os
import cv2
import numpy as np
from datetime import datetime
import re

class save:
    def __init__(self, program: str) -> None:
        self.program = program
        self.documents_folder = os.path.join("D:\\")
        self.main_folder = os.path.join(self.documents_folder, "TW")
        self.sub_folder = os.path.join(self.main_folder, self.program)
        self.date_folder = os.path.join(self.sub_folder, datetime.today().strftime('%y%m%d'))
        self.num = self.get_last_num(self.date_folder) + 1

    def get_last_num(self, folder):
        try:
            file_list = os.listdir(folder)
            num_list = [int(re.findall(r'\d+', i)[0]) for i in file_list if re.findall(r'\d+', i)]
            return max(num_list)
        except:
            return 0

    def unit_folder_edit(self, defect_name: str):
        self.unit_folder = os.path.join(self.date_folder, defect_name)
        if not os.path.exists(self.unit_folder):
            os.mkdir(self.unit_folder)

    def nut_image_save(self, frame: np.ndarray, defects_name: str, ssim_value: float):
        self.unit_folder_edit(defects_name)

        unit_name = str(round(ssim_value,4)).replace(".","_")
        # 폴더가 이미 존재하는지 확인 후 생성
        for f in [self.main_folder, self.sub_folder, self.date_folder, self.unit_folder]:
            if not os.path.exists(f):
                os.mkdir(f)

        filename = f"{self.num}_{unit_name}.png"
        photo_path = os.path.join(self.date_folder, filename)
        cv2.imwrite(photo_path, frame)
        self.num += 1
