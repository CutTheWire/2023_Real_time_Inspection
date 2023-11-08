import os
import xml.etree.ElementTree as ET
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split

# 경로 설정
data_dir = 'dataset/train'
img_dir = os.path.join(data_dir, 'images')
annot_dir = os.path.join(data_dir, 'annotations')

# 클래스 레이블 정의 (라벨에 따라 조정)
class_labels = {'nut': 0, 'none': 1}

# 데이터 수집
images = []
labels = []

# XML 주석 파싱 및 데이터 수집
for xml_file in os.listdir(annot_dir):
    tree = ET.parse(os.path.join(annot_dir, xml_file))
    root = tree.getroot()

    image_path = os.path.join(img_dir, root.find('filename').text)
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    images.append(image)

    # 클래스 레이블을 수정하여 "nut" 클래스에 속하는 이미지의 라벨을 0, 다른 클래스에 속하는 이미지의 라벨을 1로 설정
    class_name = root.find('object').find('name').text
    if class_name == 'nut':
        label = 0
    else:
        label = 1
    labels.append(label)

images = np.array(images)
labels = np.array(labels)

# 데이터 분할 (필요에 따라 학습 및 검증 데이터를 나눌 수 있음)
# images, _, labels, _ = train_test_split(images, labels, test_size=0.2, random_state=42)

# ResNet50 모델 로드
base_model = ResNet50(weights='imagenet', include_top=False)
GAP_layer = GlobalAveragePooling2D()
output_layer = Dense(len(class_labels), activation='softmax')

model = Sequential([
    base_model,
    GAP_layer,
    output_layer
])

# 데이터 전처리 및 학습 설정
images = preprocess_input(images)
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 모델 학습
model.fit(images, labels, epochs=1)

# 모델 저장
model.save("object_detection_model.h5")
