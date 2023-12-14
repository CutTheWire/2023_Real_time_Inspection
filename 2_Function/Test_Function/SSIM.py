import cv2
import numpy as np
import base64
import os
from PIL import Image
import matplotlib.pyplot as plt
import pytorch_msssim
import torchvision.transforms as transforms

# base64 데이터를 불러옵니다.
with open('C:\\Users\\sjmbe\\TW\\NUT\\1_avg_img_base64.txt', 'r') as f:
    base64_data = f.read()

# base64 데이터를 이미지로 변환합니다.
img_data = base64.b64decode(base64_data)
nparr = np.frombuffer(img_data, np.uint8)
img_chisqr = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
base64_height, base64_width = img_chisqr.shape

# 이미지를 PyTorch 텐서로 변환합니다.
transform = transforms.Compose([transforms.ToTensor()])
img_chisqr = Image.fromarray(img_chisqr)
img_chisqr = transform(img_chisqr).unsqueeze(0)

# 비교할 이미지 디렉토리 설정
compare_dir = "C:\\Users\\sjmbe\\TW\\NUT\\231108\\1-1"
compare_files = [f for f in os.listdir(compare_dir) if os.path.isfile(os.path.join(compare_dir, f))]
# 각 이미지의 파일 이름과 SSIM 값을 저장할 두 개의 리스트를 생성합니다.
file_names = []
ssim_values = []
# 각 이미지에 대해
for compare_file in compare_files:
    # 이미지를 불러옵니다.
    img_compare = cv2.imread(os.path.join(compare_dir, compare_file), cv2.IMREAD_GRAYSCALE)
    img_height, img_width = img_compare.shape

    if img_width > base64_width:
        img_compare = img_compare[:, 0:base64_width]

    elif img_height > base64_height:
        # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
        img_compare = img_compare[0:base64_height, :]

    elif img_width >= base64_width and img_height >= base64_height:
        # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
        img_compare = img_compare[0:base64_height, 0:base64_width]
    img_compare = cv2.resize(img_compare, (base64_width, base64_height))

    # 이미지를 PyTorch 텐서로 변환합니다.
    img_compare = Image.fromarray(img_compare)
    img_compare = transform(img_compare).unsqueeze(0)

    # CW-SSIM을 계산합니다.
    ssim_value = pytorch_msssim.ssim(img_chisqr, img_compare)

    # 파일 이름과 SSIM 값을 리스트에 추가합니다.
    file_names.append(compare_file)
    ssim_values.append(ssim_value.item()*100)

# SSIM 값을 선 그래프로 표시합니다.
plt.figure(figsize=(10,5))
plt.plot(file_names, ssim_values, marker='o')
plt.xlabel('Image File')
plt.ylabel('SSIM Value')
plt.title('SSIM Values of Images Compared to Base64 Image')
plt.xticks(rotation=90)  # x축 레이블을 90도 회전하여 보기 쉽게 만듭니다.
plt.tight_layout()
plt.show()