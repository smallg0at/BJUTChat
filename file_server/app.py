from flask import Flask, request, jsonify, send_file
import os
import uuid
import sqlite3
import time
import hashlib
import zipfile
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 设置文件大小限制为100MB

# sqlite 实例
if not os.path.exists('file_server/database.db'):
    print("You're probably on the wrong working directory!")



# 确保上传文件夹存在
if not os.path.exists(f'file_server/{UPLOAD_FOLDER}'):
    os.makedirs(f'file_server/{UPLOAD_FOLDER}')

def allowed_file(filename):
    return True

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'file too large'}), 413

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Request files:", request.files)
    
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
        print("Saving file to:", file_path)
        file.save(file_path)
        print("File saved successfully.")

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
        print("File info inserted into database.")

        return jsonify({'file_id': file_id}), 200

    return jsonify({'error': 'file not allowed'}), 400

def insert_into_database(file_info):
    conn = sqlite3.connect('file_server/database.db')
    print("Database connection established.")
    c = conn.cursor()
    print("Cursor created.")
    c.execute('''
        INSERT INTO files (id, upload_time, is_deleted) 
        VALUES (?, ?, ?)
    ''', (file_info['id'], file_info['upload_time'], file_info['is_deleted']))
    conn.commit()
    print("Database commit successful.")
    conn.close()
    print("Database connection closed.")
    print("Inserted file info into database:", file_info)

def insert_upload_log(file_id, user_id, timestamp):
    conn = sqlite3.connect('file_server/database.db')
    print("Database connection established.")
    c = conn.cursor()
    print("Cursor created.")
    c.execute('''
        INSERT INTO upload_logs (file_id, user_id, timestamp)
        VALUES (?, ?, ?)
    ''',(file_id, user_id, timestamp))
    conn.commit()
    print("Database commit successful.")
    conn.close()
    print("Database connection closed.")
    print("Upload log recorded:", file_id, user_id, timestamp)


def insert_download_log(file_id, user_id, timestamp):
    conn = sqlite3.connect('file_server/database.db')
    print("Database connection established.")
    c = conn.cursor()
    print("Cursor created.")
    c.execute('''
        INSERT INTO download_logs (file_id, user_id, timestamp)
        VALUES (?, ?, ?)
    ''', (file_id, user_id, timestamp))
    conn.commit()
    conn.close()
    print("Download log recorded:", file_id, user_id, timestamp)


@app.route('/download', methods=['GET'])
def download_file():
    user_id = request.args.get('user_id', '')
    file_id = request.args.get('file_id', '')
    
    if not user_id or not file_id:
        return jsonify({'error': 'missing user_id or file_id'}), 400
    
    print("Fetching file with ID:", file_id, "for user:", user_id)

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
        print("File not found on server.")
        return jsonify({'error': 'file not found on server'}), 404

    file_md5 = calculate_md5(file_path)
    download_time = int(time.time())
    insert_download_log(file_id, user_id, download_time)

    print("File found, sending to user:", user_id)

    response = send_file(file_path_send, mimetype='application/octet-stream')
    response.headers['MD5'] = file_md5
    return response

@app.route('/download_batch', methods=['POST'])
def download_batch():
    user_id = request.json.get('user_id', '')
    file_ids = request.json.get('file_ids', [])

    if not user_id or not file_ids:
        return jsonify({'error': 'missing user_id or file_ids'}), 400

    print("Fetching files with IDs:", file_ids, "for user:", user_id)

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file_id in file_ids:
            conn = sqlite3.connect('file_server/database.db')
            c = conn.cursor()
            c.execute('SELECT * FROM files WHERE id = ?', (file_id,))
            file_record = c.fetchone()
            conn.close()

            if file_record:
                file_path = os.path.join(f"file_server/{app.config['UPLOAD_FOLDER']}", file_id)
                if os.path.exists(file_path):
                    zf.write(file_path, arcname=file_id)
                    print(f"Added file {file_id} to ZIP archive.")

                    # 记录下载日志
                    download_time = int(time.time())
                    insert_download_log(file_id, user_id, download_time)
                else:
                    print(f"File {file_id} not found on server.")
            else:
                print(f"File {file_id} not found in database.")

    memory_file.seek(0)
    print("Sending ZIP archive to user:", user_id)
    return send_file(memory_file, download_name='files.zip', mimetype='application/octet-stream', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)