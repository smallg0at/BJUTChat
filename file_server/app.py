from flask import Flask, request, jsonify
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 最多100 MB 

# 配置字典
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    # 这里可以定义允许的文件扩展名，比如：return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return True

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400

    file = request.files['file']
    user_id = request.form.get('user_id', '')

    if file.filename == '':
        return jsonify({'error': 'no selected file'}), 400

    if file and allowed_file(file.filename):
        # 生成唯一的文件名
        filename = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 生成文件ID
        file_id = str(uuid.uuid4())

        # 要存入数据库的信息
        file_info = {
            'id': file_id,
            'user_id': user_id,
            'file_name': file.filename,
            'file_path': file_path
        }

        # 存数据的函数
        insert_into_database(file_info)

        return jsonify({'file_id': file_id}), 200

    return jsonify({'error': 'file not allowed'}), 400

def insert_into_database(file_info):
    # 这里应该实现将 file_info 插入数据库的逻辑
    pass

if __name__ == '__main__':
    app.run(debug=True)
