import cv2
from typing import Tuple
import numpy as np
import base64
from PIL import Image
import pytorch_msssim
import torchvision.transforms as transforms

import DATA.base64_data as B64D
num = 0

def detect_defects(frame: np.ndarray) -> Tuple[int, float]:
    global num
    # base64 데이터를 이미지로 변환합니다.
    img_data = base64.b64decode(B64D.Avg_image_base64)
    nparr = np.frombuffer(img_data, np.uint8)
    img_chisqr = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    base64_height, base64_width = img_chisqr.shape

    # 이미지를 PyTorch 텐서로 변환합니다.
    transform = transforms.Compose([transforms.ToTensor()])
    img_chisqr = Image.fromarray(img_chisqr)
    img_chisqr = transform(img_chisqr).unsqueeze(0)

    img_height, img_width = frame.shape

    if img_width > base64_width:
        frame = frame[:, 0:base64_width]

    elif img_height > base64_height:
        # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
        frame = frame[0:base64_height, :]

    elif img_width >= base64_width and img_height >= base64_height:
        # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
        frame = frame[0:base64_height, 0:base64_width]
    frame = cv2.resize(frame, (base64_width, base64_height))

    del img_height, img_width, base64_width, base64_height

    # 이미지를 PyTorch 텐서로 변환합니다.
    frame = Image.fromarray(frame)
    frame = transform(frame).unsqueeze(0)

    # CW-SSIM을 계산합니다.
    ssim_value = pytorch_msssim.ssim(img_chisqr, frame)
    ssim_value = ssim_value.item()*100
    del img_chisqr, frame
    
    if 97.65 < ssim_value:
        return 1, ssim_value
    elif 97.45 >= ssim_value and 97.25 < ssim_value:
        return 2, ssim_value
    else:
        return 0, ssim_value


# def detect_defects(frame: np.ndarray) -> Tuple[int, float]:
#     global num
#     # base64 데이터를 이미지로 변환합니다.
#     img_data = base64.b64decode(B64D.Avg_image_base64)
#     img_data_2 = base64.b64decode(B64D.Avg_image_base64_2)
#     nparr = np.frombuffer(img_data, np.uint8)
#     img_chisqr = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
#     base64_height, base64_width = img_chisqr.shape

#     nparr_2 = np.frombuffer(img_data_2, np.uint8)
#     img_chisqr_2 = cv2.imdecode(nparr_2, cv2.IMREAD_GRAYSCALE)
#     base64_height_2, base64_width_2 = img_chisqr_2.shape

#     # 이미지를 PyTorch 텐서로 변환합니다.
#     transform = transforms.Compose([transforms.ToTensor()])
#     img_chisqr = Image.fromarray(img_chisqr)
#     img_chisqr = transform(img_chisqr).unsqueeze(0)

#     img_chisqr_2 = Image.fromarray(img_chisqr_2)
#     img_chisqr_2 = transform(img_chisqr_2).unsqueeze(0)

#     img_height, img_width = frame.shape

#     if img_width > base64_width:
#         frame = frame[:, 0:base64_width]

#     elif img_height > base64_height:
#         # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
#         frame = frame[0:base64_height, :]

#     elif img_width >= base64_width and img_height >= base64_height:
#         # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
#         frame = frame[0:base64_height, 0:base64_width]
#     frame = cv2.resize(frame, (base64_width, base64_height))

#     frame_2 = frame.copy()

#     if img_width > base64_width_2:
#         frame_2 = frame_2[:, 0:base64_width_2]

#     elif img_height > base64_height_2:
#         # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
#         frame_2 = frame_2[0:base64_height_2, :]

#     elif img_width >= base64_width_2 and img_height >= base64_height_2:
#         # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
#         frame_2 = frame_2[0:base64_height_2, 0:base64_width_2]
#     frame_2 = cv2.resize(frame_2, (base64_width_2, base64_height_2))

#     del img_height, img_width, base64_width, base64_height, base64_width_2, base64_height_2

#     # 이미지를 PyTorch 텐서로 변환합니다.
#     frame = Image.fromarray(frame)
#     frame = transform(frame).unsqueeze(0)

#     frame_2 = Image.fromarray(frame_2)
#     frame_2 = transform(frame_2).unsqueeze(0)

#     # CW-SSIM을 계산합니다.
#     ssim_value = pytorch_msssim.ssim(img_chisqr, frame)
#     ssim_value = ssim_value.item() * 100
#     del img_chisqr, frame

#     ssim_value_2 = pytorch_msssim.ssim(img_chisqr_2, frame_2)
#     ssim_value_2 = ssim_value_2.item() * 100
#     del img_chisqr_2, frame_2

#     if ssim_value > ssim_value_2:
#         if 97.65 < ssim_value:
#             return 1, ssim_value
#         elif 97.45 >= ssim_value and 97.25 < ssim_value:
#             return 2, ssim_value
#     else:
#         if 97.65 < ssim_value_2:
#             return 1, ssim_value_2
#         elif 97.45 >= ssim_value_2 and 97.25 < ssim_value_2:
#             return 2, ssim_value_2

#     return 0, max(ssim_value, ssim_value_2)
