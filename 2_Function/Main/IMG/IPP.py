# Image Pre-Processing
import cv2
import numpy as np
from PIL import Image, ImageTk

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
        if len(image.shape) == 1:
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

    def Pos_by_Img(self, image, pos):
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
        # 이미지를 그레이스케일로 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 임계값 설정 (70 이하인 부분만 선택)
        _, mask = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)
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

    def image_tk(self, video_label_image):
        image_tk = ImageTk.PhotoImage(
                        Image.fromarray(
                            cv2.cvtColor(video_label_image, cv2.COLOR_BGR2RGB)
                        )) # PIL 이미지를 Tkinter PhotoImage 객체로 변환
        return image_tk

    def edit(self, frame: np.ndarray, num: tuple) -> np.ndarray:
        x, y, w, h = num
        wp = int(w*0.19)
        hp1 = int(h*0.09)
        hp2 = int(h*0.29)
        framea = frame[y+hp1:(y+h)-hp2, x+wp:(x+w)-wp]
        return framea
'''
-------------------------------------------테스트-------------------------------------------
'''

# if __name__ == "__main__":
#     image = cv2.imread("C:/Users/sjmbe/TW/TEST/230908/161906_Micro.jpg")
#     IC = ImageCV()
#     cv2.imshow("test",IC.Binarization(IC.Brightness(image)))
#     cv2.waitKey(0)
