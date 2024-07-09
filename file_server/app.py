from flask import Flask, request, jsonify
import os
import uuid
import sqlite3
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    # 这里可以定义允许的文件扩展名
    return True

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'no selected file'}), 400

    if file and allowed_file(file.filename):
        # 生成唯一的文件名作为文件ID，不加扩展名
        file_id = str(uuid.uuid4())
        filename = file_id
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
    conn = sqlite3.connect('server/database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO files (id, upload_time, is_deleted) 
        VALUES (?, ?, ?)
    ''', (file_info['id'], file_info['upload_time'], file_info['is_deleted']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
