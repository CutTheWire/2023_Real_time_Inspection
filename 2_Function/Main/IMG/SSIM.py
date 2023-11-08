import cv2
import numpy as np
import base64
import os
from PIL import Image
from torch.autograd import Variable
import torch
import pytorch_msssim
import torchvision.transforms as transforms

import DATA.base64_data as B64D

def detect_defects(frame: np.ndarray):
    # base64 데이터를 이미지로 변환합니다.
    img_data = base64.b64decode(B64D.Avg_image_base64)
    nparr = np.frombuffer(img_data, np.uint8)
    img_chisqr = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    base64_height, base64_width = 225, 284

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

    # 이미지를 PyTorch 텐서로 변환합니다.
    frame = Image.fromarray(frame)
    frame = transform(frame).unsqueeze(0)

    # CW-SSIM을 계산합니다.
    ssim_value = pytorch_msssim.ssim(img_chisqr, frame)

    if 98.1 < ssim_value.item()*100:
        return 1
    else:
        return 0
