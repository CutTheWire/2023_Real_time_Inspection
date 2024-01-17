# Image Pre-Processing
import os
import cv2
import copy
import numpy as np
from PIL import Image, ImageTk
from typing import Tuple, Union, Any
from datetime import datetime
import re

class save:
    def __init__(self, program: str) -> None:
        self.program = program
        self.documents_folder = os.path.join("C:\\")
        self.main_folder = os.path.join(self.documents_folder, "TW")
        self.sub_folder = os.path.join(self.main_folder, self.program)
        self.date_folder = os.path.join(self.sub_folder, datetime.today().strftime('%y%m%d'))
        self.num = self.get_last_num(self.date_folder) + 1

    def get_last_num(self, folder: str) -> None:
        try:
            file_list = os.listdir(folder)
            num_list = [int(re.findall(r'\d+', i)[0]) for i in file_list if re.findall(r'\d+', i)]
            return max(num_list)
        except:
            return 0

    def nut_image_save(self, frame: np.ndarray, defects_name: str, ssim_value: float) -> None:
        self.unit_folder = os.path.join(self.date_folder, defects_name)
        unit_name = str(round(ssim_value,4)).replace(".","_")

        # 폴더가 이미 존재하는지 확인 후 생성
        for f in [self.main_folder, self.sub_folder, self.date_folder, self.unit_folder]:
            if not os.path.exists(f):
                os.mkdir(f)

        # 해당 디렉토리에 있는 파일 이름들을 확인하고 가장 큰 번호를 찾음
        files = os.listdir(self.unit_folder)
        if files:  # 파일이 있는 경우
            numbers = [int(file.split('(')[0]) for file in files if file.split('(')[0].isdigit()]
            if numbers:  # 숫자로 된 파일 이름이 있는 경우
                self.num = max(numbers) + 1

        filename = f"{self.num}({unit_name}).png"
        photo_path = os.path.join(self.unit_folder, filename)
        cv2.imwrite(photo_path, frame)
        self.num += 1


class ImageCV:
    def __init__(self) -> None:
        self.brigtness = -30 #양수 밝게, 음수 어둡게
        self.alp = 1.0
        self.kernel_3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        self.kernel_5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        self.kernel_ones = np.ones((3,3),np.uint8)

        # set_brightness_threshold
        self.threshold = 0

    def gray(self, image: np.ndarray) -> np.ndarray:
        '''
        이미지의 채널 수로 흑백 여부 판단\n
        Input : 이미지 | Output : 흑백 이미지
        '''
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        return gray_image
    
    def BGR(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 2:
            BGR_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            BGR_image = image
        return BGR_image

    def Image_Crop(self, image, pos: np.ndarray, dsize: tuple) -> np.ndarray:
        dst = cv2.warpPerspective(image, pos, dsize)
        return cv2.flip(dst, 0)
    
    def Scale_Resolution(self, image: np.ndarray, Scale: float) -> tuple:
        height, width = image.shape[:2]
        return (int(width*Scale), int(height*Scale))
    
    def Image_Slice(self, image: np.ndarray, height_value: float, width_value: float) -> np.ndarray:
        height, width = image.shape[:2]
        fix_value = [0,0]
        values = [height_value, width_value]

        for i in range(len(values)):
            if values[i] <= 0.01 and values[i] > 0:
                fix_value[i] = 0

            elif values[i] > 0.01:
                fix_value[i] = 0.01

            elif values[i] <= 0:
                values[i] = 0
                fix_value[i] = 0
            
        return image[int(height*(values[0]+fix_value[0])):int(height*(1-values[0]+fix_value[0])):
                    ,int(width*values[1]):int(width*(1-values[1]+fix_value[1]))]
    
    def Brightness(self, image: np.ndarray) -> np.ndarray:
        image = (np.int16(image) + self.brigtness).astype(np.uint8)
        return image
    
    def Dilate(self, image: np.ndarray) -> np.ndarray:
        image = np.clip((1.0+self.alp) * image - 128 * self.alp, 0, 255)
        image = cv2.dilate(image,self.kernel_5, iterations = 1)
        return image
    
    def Binarization(self, image: np.ndarray) -> np.ndarray:
        image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        
        return

    def Pos_by_Img(self, image: np.ndarray, pos: np.ndarray) -> np.ndarray:
        image = self.Image_Crop(image, pos, (900,1200))
        image = self.Image_Slice(image, height_value=0.02, width_value=0.02)
        image = self.Brightness(image)

        result_image_Resolution = self.Scale_Resolution(image, 0.5)
        image = cv2.resize(image, result_image_Resolution)
        return image

    def Histogram_Equalization(self, image: np.ndarray) -> np.ndarray:
        '''
        Input: 이미지\n
        Output: 히스토그램 평활화된 이미지
        '''
        # Convert the image to grayscale if it's not already
        gray_image = self.gray(image)
        # Apply histogram equalization
        equalized_image = cv2.equalizeHist(gray_image)

        return equalized_image

    def Contrast_Adjustment(self, image: np.ndarray) -> np.ndarray:
        alpha = 1.5  # Adjust the contrast factor
        # Apply the contrast adjustment formula
        dst = cv2.convertScaleAbs(image, alpha=alpha, beta=(1 - alpha) * 128)
        return dst
    
    def highlight_contours(self, image: np.ndarray, contours: np.ndarray) -> np.ndarray:
        '''
        Input : 이미지, 윤곽선\n
        Output : 윤곽선 이외 지역 흰색으로 변경된 이미지
        '''
        # Create a mask for the contour regions
        mask = np.zeros_like(image)

        # Draw the contours on the mask
        cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

        # Create an inverse mask to keep the areas outside the contours
        inverse_mask = 255 - mask

        # Set the areas outside the contours to white in the original image
        image[inverse_mask == 255] = 255

        return image
    
    def color_invert(self, image: np.ndarray) -> np.ndarray:
        inverted_image = 255 - image
        return inverted_image
    
    def threshold_brightness(self, image: np.ndarray, threshold: int) -> np.ndarray:
        '''
        이미지의 임계값(threshold) 이하의 밝기를 검은색(0)으로 변경\n
        Input : 이미지, 임계값 | Output : 밝기 조정된 이미지
        '''
        gray_image = self.gray(image)
        # Apply the threshold to set pixels below the threshold to black
        _, thresholded_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)
        return thresholded_image
    
    def Mask(self, image: np.ndarray, thresh: np.ndarray) -> np.ndarray:
        '''
        Input : 원본 이미지, 추출 이미지\n
        Output : 마스크 이미지
        '''
        # 임계값 설정
        _, mask = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY_INV)
        return mask
    
    def Background_Area(self, image: np.ndarray) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        image = self.gray(image)
        dist = cv2.distanceTransform(image, cv2.DIST_L2, 5)
        # foreground area
        _, sure_fg = cv2.threshold(dist, 0.46* dist.max(), 255, cv2.THRESH_BINARY)
        sure_bg = cv2.dilate(sure_fg, kernel, iterations=1)
        sure_bg = sure_bg.astype(np.uint8)
        return sure_bg
    
    def Image_empty(self, image: np.ndarray) -> np.ndarray:
        height, width, channels = image.shape
        # 상단에 추가할 빈 공간의 높이 설정
        top_padding = height//12  # 원하는 높이로 설정
        # 여백을 추가할 새로운 이미지 생성
        new_height = height + top_padding
        new_image = np.zeros((new_height, width, channels), dtype=np.uint8)
        # 기존 이미지를 새로운 이미지의 아래로 복사
        new_image[top_padding:, :] = image
        return new_image

    def image_tk(self, video_label_image: np.ndarray) -> np.ndarray:
        image_tk = ImageTk.PhotoImage(
                        Image.fromarray(
                            cv2.cvtColor(video_label_image, cv2.COLOR_BGR2RGB)
                        )) # PIL 이미지를 Tkinter PhotoImage 객체로 변환
        return image_tk

    def edit(self, frame: np.ndarray, num: tuple) -> np.ndarray:
        x, y, w, h = num
        wp = int(w*0.25)
        hp1 = int(h*0.18)
        hp2 = int(h*0.31)
        framea = frame[y+hp1:(y+h)-hp2, x+wp:(x+w)-wp]
        return framea

class object_get:
    def __init__(self) -> None:
        self.last_counted_time = None
        self.min_contour_size = 10000
        self.max_contour_size = 500000
        self.sub_line_y = 150
        self.sub_line_x = 600

    def get(self, frame: np.ndarray, width: int, height: int, num_max: int, num_min: int) -> Union[Tuple[np.ndarray, int], Tuple[np.ndarray, tuple]]:
        horizontal_line_y = height // 2
        gray = copy.deepcopy(frame[(horizontal_line_y-self.sub_line_y):,self.sub_line_x:-self.sub_line_x])
        edit_gray = copy.copy(gray)
        # 조건에 맞는 픽셀 값 변경
        gray[np.where((gray < num_min) | (gray > num_max))] = 0

        contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = list(filter(lambda cnt: cv2.contourArea(cnt) >= self.min_contour_size and cv2.contourArea(cnt) <= self.max_contour_size, contours))
        
        # 수직선 그리기
        cv2.line(frame, (self.sub_line_x, horizontal_line_y- self.sub_line_y), (self.sub_line_x, height), (255, 255, 255), 2)  # 왼쪽 수직선
        cv2.line(frame, (width - self.sub_line_x, horizontal_line_y- self.sub_line_y), (width - self.sub_line_x, height), (255, 255, 255), 2)  # 오른쪽 수직선
        
        # 수평선 그리기
        cv2.line(frame, (0, horizontal_line_y), (width, horizontal_line_y), (0, 0, 255), 2)
        cv2.line(frame, (0, horizontal_line_y - self.sub_line_y), (width, horizontal_line_y - self.sub_line_y), (0, 255, 255), 2)


        if contours:  # contours 리스트가 비어있지 않은 경우에만 실행
            contour = max(contours, key=cv2.contourArea)  # 가장 큰 윤곽선 선택
            hull = cv2.convexHull(contour)

            # frame 전체에 대해 윤곽선 그리기
            cv2.drawContours(frame[horizontal_line_y-self.sub_line_y:, self.sub_line_x:-self.sub_line_x], [hull], -1, (0, 255, 0), 3)

            min_y = np.min(hull[:, :, 1]) + horizontal_line_y - self.sub_line_y  # 슬라이싱으로 잘린 부분만큼 y축 위치를 보정
            if min_y <= horizontal_line_y and min_y >= horizontal_line_y - self.sub_line_y:
                current_time = datetime.now()

                if self.last_counted_time is None or (current_time - self.last_counted_time).total_seconds() > 1.6:
                    self.last_counted_time = current_time
                    del current_time
                    x, y, w, h = cv2.boundingRect(hull)
                    # 윤곽선 이미지 추출
                    edit_frame = edit_gray[y+int(h*0.2):y+h-int(h*0.3), x+int(w*0.2):x+w-int(w*0.2)].copy()

                    return frame, (x, y, w, h), edit_frame, gray
        return frame, 0, None, gray

'''
-------------------------------------------테스트-------------------------------------------
'''

# if __name__ == "__main__":
#     image = cv2.imread("C:/Users/sjmbe/TW/TEST/230908/161906_Micro.jpg")
#     IC = ImageCV()
#     cv2.imshow("test",IC.Binarization(IC.Brightness(image)))
#     cv2.waitKey(0)
