# import tensorflow as tf

# # GPU 디바이스 리스트 가져오기
# gpus = tf.config.experimental.list_physical_devices('GPU')

# # GPU 디바이스 출력 및 모델 이름 확인
# for gpu in gpus:
#     print("GPU 디바이스 이름:", gpu.name)
#     device_desc = tf.config.experimental.get_device_details(gpu)
#     print("GPU 모델 이름:", device_desc['device_name'])


from tensorflow.python.client import device_lib
import torch
DEVICE = ("cuda" if torch.cuda.is_available() else "cpu")
print(DEVICE)