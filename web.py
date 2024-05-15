from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import numpy as np

from ai import face_processing


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sipresen_db'
mysql = MySQL(app)

UPLOAD_FOLDER = 'static/upload/img_register'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}




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
     # Mendeteksi apakah perangkat adalah perangkat mobile
    user_agent = request.headers.get('User-Agent').lower()
    is_mobile = any(mobile in user_agent for mobile in ['iphone', 'android', 'blackberry', 'opera mini', 'windows mobile'])
    if is_mobile:
        return render_template('login.html',menu='login')
    else:
        return render_template('mobile-only.html')
@app.route("/loginkelas", methods=["POST", "GET"])
def loginkelas():
    try:
        if 'gambarWajah' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'})
        
        token = request.form.get('tokenKelas')
        file = request.files['gambarWajah']

        img_np = np.fromstring(file.read(), np.uint8)
        # img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        face_verify = face_processing(img_np)
        

        if face_verify == "you are not registered yet":
            response = {'success': False, 'message': 'you are not registered yet'}
            return jsonify(response), 400        
        if face_verify == "More than 1 face detected":
            response = {'success': False, 'message': 'More than 1 face detected'}
            return jsonify(response), 400
        if face_verify == "there is no one face detected":
            response = {'success': False, 'message': 'there is no one face detected'}
            return jsonify(response), 400
        if face_verify == "fake":
            response = {'success': False, 'message': 'fake'}
            return jsonify(response), 400

        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'})
        
        if token and file and allowed_file(file.filename) and face_verify:  # Memastikan semua data diterima
            img_login = face_verify.split('\\')[1]

            try:
                cur = mysql.connection.cursor()
                query = "SELECT name From students_registered WHERE file LIKE %s"
                cur.execute(query, (img_login,))
                # Mengambil hasil query
                data = cur.fetchall() #type data tuple
                cur.close()
                if data is not None:
                    namalengkap = str(data[0])
                    panggilan = namalengkap.split("'")[1]
                    filename = secure_filename(str(panggilan) + "_login_" + str(token)) + ".jpg"  # Ganti ekstensi sesuai kebutuhan

                    uploads_folder = os.path.join(os.getcwd(), 'static', 'upload/img_login')

                    file_path = os.path.join(uploads_folder, filename)  # Path penyimpanan file
                    with open(file_path, 'wb') as f:  # Mode 'wb' untuk menyimpan dalam mode biner
                        f.write(img_np)  # Menulis konten byte ke file

                    response = {'success': True, 'message': 'successfull', 'name': panggilan}
                    return jsonify(response)
                else:
                    response = {'success': False, 'message': 'gada didaftar db!'}
                    return jsonify(response)
            except Exception as e:
                response = {'success': False, 'message': str(e)}
                return jsonify(response), 500
        else:
            response = {'success': False, 'message': 'Missing required data'}
            return jsonify(response), 400  # Mengembalikan kode status 400 (Bad Request) jika data yang diperlukan tidak ditemukan
    except:
        response = {'success': False, 'message': 'form kosong'}
        return jsonify(response), 400   
    
@app.route('/table')
def table():
    return render_template('table.html',menu='table')
@app.route('/generate')
def generate():
    return render_template('generate.html',menu='generate')
@app.route("/generatetoken", methods=["POST", "GET"])
def generatetoken():
    try:
        email = request.form.get('email')
        nama = request.form.get('nama')
        inisial = request.form.get('inisial')
        nip = request.form.get('nip')
        matkul = request.form.get('matkul')
        pertemuan = request.form.get('pertemuan')
        tanggal = request.form.get('tanggal')
        waktu = request.form.get('waktu')
        deskripsi = request.form.get('deskripsi')
        token = request.form.get('token')
        # token = 549567
        
        if email and nama and inisial and nip and matkul and pertemuan and tanggal and waktu and deskripsi and token:
            try:
                cur = mysql.connection.cursor()
                query = "SELECT token From data_token WHERE token LIKE %s"
                cur.execute(query, (token,))
                # Mengambil hasil query
                data = cur.fetchall() #type data tuple
                cur.close()
                if data and data[0][0] == token:
                    response = {'success': False, 'message': 'token is existing'}
                    return jsonify(response), 400
                else:
                    try:
                        cur = mysql.connection.cursor()
                        cur.execute("INSERT INTO data_token(email,name,initial,nip,subject,meeting,date,time,description,token) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (email,nama,inisial,nip,matkul,pertemuan,tanggal,waktu,deskripsi,token))
                        mysql.connection.commit()
                        cur.close()
                        response = {'success': True, 'message': 'successfull', 'token': token}
                        return jsonify(response)
                    except:
                        response = {'success': False, 'message': 'gagal pas di mysql'}
                        return jsonify(response), 500  # Mengembalikan kode status 500 (Internal Server Error) jika terjadi kesalahan
            except Exception as e:
                print(f"Error during fetching token from database: {e}")
                response = {'success': False, 'message': 'gagal pas di mysql token'}
                return jsonify(response), 500  # Mengembalikan kode status 500 (Internal Server Error) jika terjadi kesalahan
        else:
            response = {'success': False, 'message': 'Missing required data'}
            return jsonify(response), 400
    except:
        response = {'success': False, 'message': 'form kosong'}
        return jsonify(response), 400 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
