import cv2
from skimage.metrics import structural_similarity as ssim

# 이미지 불러오기
image1 = cv2.imread('C:\\TW\\NUT\\231215\\X\\381(0).png', cv2.IMREAD_GRAYSCALE)
image2 = cv2.imread('C:\\TW\\NUT\\231215\\X\\373(0).png', cv2.IMREAD_GRAYSCALE)


# 두 이미지의 크기를 동일하게 조정
height, width = image1.shape
image2 = cv2.resize(image2, (width, height))

# SSIM 계산
ssim_value = ssim(image1, image2)

print("SSIM: ", ssim_value)
