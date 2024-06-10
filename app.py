# import tensorflow as tf
# print("TensorFlow version:", tf.__version__)
# print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

from deepface import DeepFace

# anti spoofing test in face detection
face_objs = DeepFace.extract_faces(
  img_path="3.jpg",
  anti_spoofing = True
)
# assert all(face_obj["is_real"] is True for face_obj in face_objs)
print(face_objs[0])

for face_obj in face_objs:
    is_real_value = face_obj['is_real']
    if is_real_value:
        print('ini asli')
    else:
        print('palsuuu')

#face recognition
dfs = DeepFace.find(
  img_path = "3.jpg",
  db_path = "static/upload/img_register",
)

print(dfs)