from flask import Flask, render_template, request, jsonify, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import numpy as np

from ai import face_processing


app = Flask(__name__)
app.secret_key = "supersecretkey"  # Anda harus mengatur kunci rahasia untuk sesi Flask

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
        
# @app.route("/loginkelas", methods=["POST", "GET"])
# def loginkelas():
#     try:
#         if 'gambarWajah' not in request.files:
#             return jsonify({'success': False, 'message': 'No file part'})
        
#         token = request.form.get('tokenKelas')
#         file = request.files['gambarWajah']

#         img_np = np.fromstring(file.read(), np.uint8)
#         # img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
#         face_verify = face_processing(img_np)
        

#         if face_verify == "you are not registered yet":
#             response = {'success': False, 'message': 'you are not registered yet'}
#             return jsonify(response), 400        
#         if face_verify == "More than 1 face detected":
#             response = {'success': False, 'message': 'More than 1 face detected'}
#             return jsonify(response), 400
#         if face_verify == "there is no one face detected":
#             response = {'success': False, 'message': 'there is no one face detected'}
#             return jsonify(response), 400
#         if face_verify == "fake":
#             response = {'success': False, 'message': 'fake'}
#             return jsonify(response), 400

#         if file.filename == '':
#             return jsonify({'success': False, 'message': 'No selected file'})
        
#         if token and file and allowed_file(file.filename) and face_verify:  # Memastikan semua data diterima
#             img_login = face_verify.split('\\')[1]

#             try:
#                 cur = mysql.connection.cursor()
#                 query = "SELECT name From students_registered WHERE file LIKE %s"
#                 cur.execute(query, (img_login,))
#                 # Mengambil hasil query
#                 data = cur.fetchall() #type data tuple
#                 cur.close()
#                 if data is not None:
#                     namalengkap = str(data[0])
#                     panggilan = namalengkap.split("'")[1]
#                     filename = secure_filename(str(panggilan) + "_login_" + str(token)) + ".jpg"  # Ganti ekstensi sesuai kebutuhan

#                     uploads_folder = os.path.join(os.getcwd(), 'static', 'upload/img_login')

#                     file_path = os.path.join(uploads_folder, filename)  # Path penyimpanan file
#                     with open(file_path, 'wb') as f:  # Mode 'wb' untuk menyimpan dalam mode biner
#                         f.write(img_np)  # Menulis konten byte ke file

#                     response = {'success': True, 'message': 'successfull', 'name': panggilan}
#                     return jsonify(response)
#                 else:
#                     response = {'success': False, 'message': 'gada didaftar db!'}
#                     return jsonify(response)
#             except Exception as e:
#                 response = {'success': False, 'message': str(e)}
#                 return jsonify(response), 500
#         else:
#             response = {'success': False, 'message': 'Missing required data'}
#             return jsonify(response), 400  # Mengembalikan kode status 400 (Bad Request) jika data yang diperlukan tidak ditemukan
#     except:
#         response = {'success': False, 'message': 'form kosong'}
#         return jsonify(response), 400   
    
# Fungsi untuk validasi token kelas
@app.route("/validate_token", methods=["POST"])
def validate_token():
    token = request.json.get("tokenKelas")
    if token:
        try:
            cur = mysql.connection.cursor()
            query = "SELECT token From data_token WHERE token LIKE %s"
            cur.execute(query, (token,))
            # Mengambil hasil query
            data = cur.fetchall() #type data tuple
            cur.close()
            if data and data[0][0] == int(token):
                session['token'] = token  # Simpan token dalam sesi
                response = {"status": "valid", "token": token, "success": True, "message": "token valid"}
                return jsonify(response), 200
            else:
                response = {"status": "invalid", "success": False, "message": "token tidak valid"}
                return jsonify(response)
        except Exception as e:
            response = {'success': False, 'message': str(e)}
            return jsonify(response), 500
    else:
        response = {'success': False, 'message': 'token kosong'}
        return jsonify(response), 500
        
# Fungsi untuk validasi gambar wajah
@app.route("/validate_image_wajah", methods=["POST"])
def validate_image_wajah():
    # Ambil gambar dari permintaan POST
    file = request.files['file']

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    if file and allowed_file(file.filename):
        img_np = np.fromstring(file.read(), np.uint8)
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
        
        if face_verify:
            try:
                img_login = face_verify.split('\\')[1]
                
                cur = mysql.connection.cursor()
                query = "SELECT nim From students_registered WHERE file LIKE %s"
                cur.execute(query, (img_login,))
                # Mengambil hasil query
                data = cur.fetchall() #type data tuple
                cur.close()
                if data:
                    # nim_login = str(data[0]).split("'")[1]
                    nim_login = data[0][0]
                    session['nim_login'] = nim_login  # Simpan nim dalam sesi
                    response = {"status": "valid", 'success': True, 'message': 'successfull', 'nim': nim_login}
                    return jsonify(response)
                else:
                    response = {"status": "invalid", 'success': False, 'message': 'gada didaftar db!'}
                    return jsonify(response)
            except IndexError as e:
                    response = {'success': False, 'message': str(e)}
                    return jsonify(response), 500
            except Exception as e:
                    response = {'success': False, 'message': str(e)}
                    return jsonify(response), 500
    else:
        response = {'success': False, 'message': 'Missing required data'}
        return jsonify(response), 400  # Mengembalikan kode status 400 (Bad Request) jika data yang diperlukan tidak ditemukan


    # # Dapatkan nama file gambar wajah dari form data
    # file_name_wajah = file.filename
    # # Lakukan validasi nama file gambar wajah di sini
    # if file_name_wajah == "wajah.jpg":
    #     session['file_name_wajah'] = file_name_wajah  # Simpan file_name_wajah dalam sesi
    #     response = {"status": "valid", "file_name_wajah": file_name_wajah}
    #     return jsonify(response), 200
    # else:
    #     return jsonify({"status": "invalid", "message": "Invalid image file name for wajah"}), 400

# Fungsi untuk validasi gambar kelas
@app.route("/validate_image_kelas", methods=["POST"])
def validate_image_kelas():
    # Ambil gambar dari permintaan POST
    file = request.files['file']

    # Dapatkan nama file gambar kelas dari form data
    file_name_kelas = file.filename
    # Lakukan validasi nama file gambar kelas di sini
    if file_name_kelas:
        session['file_name_kelas'] = file_name_kelas  # Simpan file_name_kelas dalam sesi
        response = {"status": "valid", "message": "valid", "file": file_name_kelas}
        return jsonify(response), 200
    else:
        return jsonify({"status": "invalid", "message": "Invalid image file name for kelas"}), 400

# Fungsi untuk submit formulir login
@app.route("/loginkelas", methods=["POST", "GET"])
def login_kelas():
    token = request.form.get('token')
    wajah = request.files['gambarWajah']
    kelas = request.files['gambarKelas']
    nim_login = session.get('nim_login')
    # print(request.form)  # Debug: Cetak form data
    # print(request.files)  # Debug: Cetak files data

    # if 'token' not in request.form:
    #     return jsonify({'success': False, 'message': 'Missing token'}), 400

    # if 'wajah' not in request.files:
    #     return jsonify({'success': False, 'message': 'Missing wajah file'}), 400

    # if 'kelas' not in request.files:
    #     return jsonify({'success': False, 'message': 'Missing kelas file'}), 400


    if wajah and allowed_file(wajah.filename) and kelas and allowed_file(kelas.filename):
        try:
            filename_wajah = secure_filename(str(token) + "_wajah_" + str(nim_login)) + ".jpg"  # Ganti ekstensi sesuai kebutuhan
            filename_kelas = secure_filename(str(token) + "_kelas_" + str(nim_login)) + ".jpg"  # Ganti ekstensi sesuai kebutuhan

            uploads_folder = os.path.join(os.getcwd(), 'static', 'upload/img_login')

            wajah_np = np.fromstring(wajah.read(), np.uint8)
            kelas_np = np.fromstring(kelas.read(), np.uint8)

            file_path_wajah = os.path.join(uploads_folder, filename_wajah)  # Path penyimpanan file
            with open(file_path_wajah, 'wb') as f:  # Mode 'wb' untuk menyimpan dalam mode biner
                f.write(wajah_np)  # Menulis konten byte ke file

            file_path_kelas = os.path.join(uploads_folder, filename_kelas)  # Path penyimpanan file
            with open(file_path_kelas, 'wb') as f:  # Mode 'wb' untuk menyimpan dalam mode biner
                f.write(kelas_np)  # Menulis konten byte ke file

            name = "ngetes_idos"
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO students_login(nim,names,tokens,face_images,class_images) VALUES(%s,%s,%s,%s,%s)", (nim_login,name,token,filename_wajah,filename_kelas))
            mysql.connection.commit()
            cur.close()
            
            response = {"status": "valid", 'success': True, 'message': 'successfull', 'nim': nim_login, 'token': token}
            return jsonify(response), 200
        except Exception as e:
            response = {'success': False, 'message': str(e)}
            return jsonify(response), 500
    else:
        response = {'success': False, 'message': 'Missing required data'}
        return jsonify(response), 400  # Mengembalikan kode status 400 (Bad Request) jika data yang diperlukan tidak ditemukan

    #  # Ambil nilai dari sesi
    # nim_login = session.get('nim_login')
    # file_name_wajah = session.get('file_name_wajah')
    # file_name_kelas = session.get('file_name_kelas')

    # # Lakukan pemrosesan formulir dan autentikasi di sini
    # if token and file_name_wajah and file_name_kelas:
    #     return jsonify({
    #         "success": True,
    #         "message": "Login berhasil",
    #         "token": token,
    #         "file_name_wajah": file_name_wajah,
    #         "file_name_kelas": file_name_kelas
    #     }), 200
    # else:
    #     return jsonify({"success": False, "message": "Incomplete form data"}), 400

@app.route('/table')
def table():
    return render_template('table.html',menu='table')

@app.route('/generatetable', methods=["POST", "GET"])
def generatetable():
    token = request.json.get("tokenKelas")
    if token:
        try:
            cur = mysql.connection.cursor()

            query = "SELECT * FROM students_login WHERE tokens LIKE %s"
            cur.execute(query, (token,))
            # Mengambil hasil query
            dataKehadiran = cur.fetchall()

            query = "SELECT * FROM data_token WHERE token LIKE %s"
            cur.execute(query, (token,))
            # Mengambil hasil query
            dataKelas = cur.fetchall()

            if dataKehadiran and dataKelas:
                response = {"status": "valid", "dataKehadiran": dataKehadiran, "dataKelas": dataKelas, "success": True, "message": "token valid"}
                return jsonify(response), 200
            else:
                response = {"status": "invalid", "success": False, "message": "token tidak valid"}
                return jsonify(response)
        except Exception as e:
            response = {'success': False, 'message': str(e)}
            return jsonify(response), 500
    else:
        response = {'success': False, 'message': 'token kosong'}
        return jsonify(response), 500

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
