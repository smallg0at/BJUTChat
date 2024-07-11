from flask import Flask, request, jsonify, send_file
import os
import uuid
import sqlite3
import time
import hashlib

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return True

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@app.route('/upload', methods=['POST'])
def upload_file():
    
    if len(request.files) <= 0:   #确保文件名不为空
        return jsonify({'error': 'no file'}), 400
  
    file = request.files['file']  
    user_id = request.form.get('user_id', '')

    if file.filename == '':
        return jsonify({'error': 'no selected file'}), 400

    if file and allowed_file(file.filename):
        # 生成唯一的文件名作为文件ID，不加扩展名
        file_id = str(uuid.uuid4())
        filename = file_id
        file_path = os.path.join(f"file_server/{app.config['UPLOAD_FOLDER']}", filename)
        file.save(file_path)

        # 获取上传时间戳
        upload_time = int(time.time())

        # 要存入数据库的信息
        file_info = {
            'id': file_id,
            'upload_time': upload_time,
            'is_deleted': False  # 初始值为否
        }

        # 存数据的函数
        insert_into_database(file_info)

        return jsonify({'file_id': file_id}), 200

    return jsonify({'error': 'file not allowed'}), 400

def insert_into_database(file_info):
    conn = sqlite3.connect('file_server/database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO files (id, upload_time, is_deleted) 
        VALUES (?, ?, ?)
    ''', (file_info['id'], file_info['upload_time'], file_info['is_deleted']))
    conn.commit()
    conn.close()

@app.route('/download', methods=['GET'])
def download_file():
    user_id = request.args.get('user_id', '')
    file_id = request.args.get('file_id', '')
    
    if not user_id or not file_id:
        return jsonify({'error': 'missing user_id or file_id'}), 400

    conn = sqlite3.connect('file_server/database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file_record = c.fetchone()
    conn.close()

    if not file_record:
        return jsonify({'error': 'file not found'}), 404

    file_path = os.path.join(f"file_server/{app.config['UPLOAD_FOLDER']}", file_id)
    file_path_send = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found on server'}), 404

    file_md5 = calculate_md5(file_path)

    response = send_file(file_path_send, mimetype='application/octet-stream', download_name=file_id)
    response.headers['MD5'] = file_md5
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5000)
