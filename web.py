from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
from deepface import DeepFace
import cv2
import numpy as np
import mysql.connector
import argparse
import warnings
import time

from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
warnings.filterwarnings('ignore')

app = Flask(__name__)

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sipresen_db'
# app.config['MYSQL_DB'] = 'flaskadminlte_db'
mysql = MySQL(app)

UPLOAD_FOLDER = 'static/upload/img_register'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

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
    image = cv2.resize(img, (int(img.shape[0] * 3 / 4), img.shape[0]))
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

def process_image(file):
    img_np = np.fromstring(file.read(), np.uint8)
    img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    return img_cv

def face_processing(img_cv):
    
    image = cv2.imdecode(img_cv, cv2.IMREAD_COLOR)
    # image = process_image(img_cv)
    model_path = "models/res10_300x300_ssd_iter_140000.caffemodel"
    prototxt_path = "models/deploy.prototxt.txt"

    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

    
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    net.setInput(blob)
    detections = net.forward()

    face_count = 0
    confidence_above_099 = 0

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.8:
            face_count += 1
            if confidence > 0.99:
                confidence_above_099 += 1

    if face_count > 1:
        return "More than 1 face detected"
    elif face_count == 1:
        anti_fake = test(image)
        if anti_fake == 1:
            try:
                folder_img = "static/upload/img_register"
                dfs = DeepFace.find(img_path=image, db_path=folder_img)
                df_at_index_0 = dfs[0]
                min_distance = df_at_index_0['distance'].min()
                row_with_min_distance = df_at_index_0.loc[df_at_index_0['distance'] == min_distance]
                identity_of_min_distance = row_with_min_distance['identity'].values[0]
                return identity_of_min_distance
            except:
                if confidence_above_099 == 1:
                    return "you are not registered yet"
                else:
                    return "picture is not clear" 
        else:
            return "fake"
    elif face_count == 0:
        return "there is no one face detected"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def main():
    return render_template('index.html')
@app.route('/register')
def register():
     # Mendeteksi apakah perangkat adalah perangkat mobile
    user_agent = request.headers.get('User-Agent').lower()
    is_mobile = any(mobile in user_agent for mobile in ['iphone', 'android', 'blackberry', 'opera mini', 'windows mobile'])
    
    if is_mobile:
        return render_template('register.html',menu='register')
    else:
        return render_template('mobile-only.html')
    
@app.route("/registerwajah", methods=["POST", "GET"])
def registerwajah():
    try:
        if 'gambarWajah' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'})
        
        email = request.form.get('email')
        nama = request.form.get('nama')
        nim = request.form.get('nim')
        prodi = request.form.get('prodi')
        angkatan = request.form.get('angkatan')
        file = request.files['gambarWajah']
        
        img_np = np.fromstring(file.read(), np.uint8)
        face_verify = face_processing(img_np)

        if face_verify == "More than 1 face detected":
            response = {'success': False, 'message': 'More than 1 face detected'}
            return jsonify(response), 400
        if face_verify == "there is no one face detected":
            response = {'success': False, 'message': 'there is no one face detected'}
            return jsonify(response), 400
        if face_verify == "picture is not clear":
            response = {'success': False, 'message': 'picture is not clear'}
            return jsonify(response), 400
        if face_verify == "fake":
            response = {'success': False, 'message': 'fake'}
            return jsonify(response), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'})

        if email and nama and nim and prodi and angkatan and file and allowed_file(file.filename) and face_verify:  # Memastikan semua data diterima

            if face_verify == "you are not registered yet":
                try:
                    filename = secure_filename(str(nim)) + ".jpg"  # Ganti ekstensi sesuai kebutuhan
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO students_registered(email,name,nim,major,batch,file) VALUES(%s,%s,%s,%s,%s,%s)", (email,nama,nim,prodi,angkatan,filename))
                    mysql.connection.commit()
                    cur.close()

                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Path penyimpanan file
                    with open(file_path, 'wb') as f:  # Mode 'wb' untuk menyimpan dalam mode biner
                        f.write(img_np)  # Menulis konten byte ke file

                    response = {'success': True, 'message': 'successfull', 'nim': nim}
                    return jsonify(response)
                except:
                    response = {'success': False, 'message': 'gagal pas di mysql'}
                    return jsonify(response), 500  # Mengembalikan kode status 500 (Internal Server Error) jika terjadi kesalahan
            else:
                img_login = face_verify.split('\\')[1]
                try:
                    cur = mysql.connection.cursor()
                    query = "SELECT nim From students_registered WHERE file LIKE %s"
                    cur.execute(query, (img_login,))
                    data = cur.fetchall() #type data tuple
                    cur.close()
                    if data is not None:
                        response = {'success': False, 'message': 'already registered', 'nim': data}
                        return jsonify(response)
                    else:
                        response = {'success': False, 'message': 'gada didaftar db!'}
                        return jsonify(response)
                except:
                    response = {'success': False, 'message': 'error setelah face processing'}
                    return jsonify(response), 500

        else:
            response = {'success': False, 'message': 'Missing required data'}
            return jsonify(response), 400  # Mengembalikan kode status 400 (Bad Request) jika data yang diperlukan tidak ditemukan
    except:
        response = {'success': False, 'message': 'form kosong'}
        return jsonify(response), 400
   
@app.route('/login')
def login():
    return render_template('login.html',menu='login')
@app.route('/table')
def table():
    return render_template('table.html',menu='table')
@app.route('/generate')
def generate():
    return render_template('generate.html',menu='generate')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
