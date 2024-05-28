
import os
import cv2
import numpy as np
import argparse
import warnings
import time

from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL

from deepface import DeepFace
from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
warnings.filterwarnings('ignore')


def check_image(image):
    height, width, channel = image.shape
    if width/height != 3/4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    else:
        return True

def test(img):
    model_dir = "./resources/anti_spoof_models"
    device_id = 0
    model_test = AntiSpoofPredict(device_id)
    image_cropper = CropImage()
    new_height = img.shape[0]
    new_width = int(new_height * 3 / 4)
    image = cv2.resize(img, (new_width, new_height))
    # image = cv2.resize(img, (int(img.shape[0] * 3 / 4), img.shape[0]))
    result = check_image(image)
    if result is False:
        return
    image_bbox = model_test.get_bbox(image)
    prediction = np.zeros((1, 3))
    test_speed = 0
    for model_name in os.listdir(model_dir):
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        param = {
            "org_img": image,
            "bbox": image_bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            param["crop"] = False
        img = image_cropper.crop(**param)
        start = time.time()
        prediction += model_test.predict(img, os.path.join(model_dir, model_name))
        test_speed += time.time()-start
    label = np.argmax(prediction)
    value = prediction[0][label]/2
    return label

def face_processing(img_cv):
    try:
        image = cv2.imdecode(img_cv, cv2.IMREAD_COLOR)
        folder_img = "static/upload/img_register"

        img = DeepFace.extract_faces(img_path=image)
        if len(img) > 1:
            return "More than 1 face detected"
        elif len(img) == 1:
            anti_fake = test(image)
            if anti_fake == 1:
                try:
                    dfs = DeepFace.find(img_path=image, db_path=folder_img)
                    # Mengakses DataFrame pada indeks 0 dari list_of_dfs
                    df_at_index_0 = dfs[0]
                    # Temukan nilai minimum dari kolom 'distance' dalam DataFrame pada indeks 0
                    min_distance = df_at_index_0['distance'].min()
                    # Temukan baris dengan nilai minimum dalam kolom 'distance'
                    row_with_min_distance = df_at_index_0.loc[df_at_index_0['distance'] == min_distance]
                    # Ambil nilai dari kolom 'identity' pada baris tersebut
                    identity_of_min_distance = row_with_min_distance['identity'].values[0]
                    return identity_of_min_distance
                except:
                    return "you are not registered yet"
            else:
                return "fake"
    except ValueError:
        return "there is no one face detected"
    

def class_processing(image_path):
    model_path = 'keras_Model.h5'
    labels_path ='labels.txt'
    # image_path = cv2.imdecode(image, cv2.IMREAD_COLOR)
        # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)

    # Load the model
    model = load_model(model_path, compile=False)

    # Load the labels
    class_names = open(labels_path, "r").readlines()

    # Create the array of the right shape to feed into the keras model
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Load and process the image
    image = Image.open(image_path).convert("RGB")

    # Resize the image to be at least 224x224 and then crop from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    # Turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Load the image into the array
    data[0] = normalized_image_array

    # Predicts the model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    confidence_score = prediction[0][index] * 100
    class_name = class_name[2:] 
    confidence_score = round(confidence_score, 2)
    print(class_name)
    print(confidence_score)

    return class_name, confidence_score

