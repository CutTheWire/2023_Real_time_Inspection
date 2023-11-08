import os
import shutil
import random

# 데이터셋 디렉토리 경로
dataset_dir = 'dataset'  # 데이터셋의 최상위 디렉토리 경로
train_dir = 'dataset/train'  # 학습 데이터가 있는 디렉토리
validation_dir = 'dataset/validation'  # 검증 데이터를 저장할 디렉토리

# 만약 validation 디렉토리가 없다면 생성
if not os.path.exists(validation_dir):
    os.makedirs(validation_dir)

# 분할 비율 설정 (예: 학습 데이터 80%, 검증 데이터 20%)
validation_split = 0.2

# 학습 데이터의 하위 폴더(클래스) 목록 가져오기
classes = os.listdir(train_dir)

# 각 클래스의 학습 데이터를 검증 데이터로 이동
for class_name in classes:
    class_train_dir = os.path.join(train_dir, class_name)
    class_validation_dir = os.path.join(validation_dir, class_name)

    # 만약 검증 데이터 디렉토리가 없다면 생성
    if not os.path.exists(class_validation_dir):
        os.makedirs(class_validation_dir)

    # 학습 데이터 파일 목록 가져오기
    class_files = os.listdir(class_train_dir)

    # 검증 데이터셋 크기 계산
    num_validation_samples = int(validation_split * len(class_files))

    # 무작위로 선택된 학습 데이터 파일을 검증 데이터 디렉토리로 이동
    validation_samples = random.sample(class_files, num_validation_samples)
    for file_name in validation_samples:
        source_path = os.path.join(class_train_dir, file_name)
        destination_path = os.path.join(class_validation_dir, file_name)
        shutil.move(source_path, destination_path)

print("검증 데이터셋이 생성되었습니다.")
