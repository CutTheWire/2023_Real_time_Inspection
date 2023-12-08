import cv2
from typing import Tuple
import numpy as np
import base64
from PIL import Image
import pytorch_msssim
import torchvision.transforms as transforms
import os
import glob
import copy


def detect_defects(frame_a: np.ndarray) -> Tuple[int, float]:
    # 'Documents/TW' 디렉토리에서 .ini 파일들을 찾습니다.
    ini_files = glob.glob(os.path.expanduser("~\\Documents\\TW\\*.ini"))

    # ssim_value를 저장할 변수를 초기화합니다.
    max_ssim_value = 0

    # .ini 파일들에 대해
    for ini_file in ini_files:
        frame = copy.deepcopy(frame_a)
        # .ini 파일을 읽습니다.
        with open(ini_file, 'r') as f:
            img_data_base64 = f.read()

        # base64 데이터를 이미지로 변환합니다.
        img_data = base64.b64decode(img_data_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        img_chisqr = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        base64_height, base64_width = img_chisqr.shape

        # 이미지를 PyTorch 텐서로 변환합니다.
        transform = transforms.Compose([transforms.ToTensor()])
        img_chisqr = Image.fromarray(img_chisqr)
        img_chisqr = transform(img_chisqr).unsqueeze(0)

        if len(frame.shape) == 3:
            img_height, img_width, _ = frame.shape
        elif len(frame.shape) == 2:
            img_height, img_width = frame.shape
        elif len(frame.shape) == 4:
            _, _, img_height, img_width = frame.shape

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

        # ssim_value를 계산합니다.
        ssim_value = pytorch_msssim.ssim(img_chisqr, frame)
        ssim_value = ssim_value.item()*100

        # 만약 현재 ssim_value가 이전까지의 최대값보다 크면, 최대값을 갱신합니다.
        if ssim_value > max_ssim_value:
            max_ssim_value = ssim_value

    # 가장 높은 ssim_value를 target_value로 설정합니다.
    target_value = max_ssim_value
    # target_value에 따라 다른 값을 반환합니다.
    if 97.65 < target_value:
        return 1, target_value
    elif 97.65 >= target_value and 97.25 < target_value:
        return 2, target_value
    else:
        return 0, target_value
    