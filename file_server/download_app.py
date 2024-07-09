from flask import Flask, request, jsonify, send_file
import os
import sqlite3
import hashlib

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.route('/download', methods=['POST'])
def download_file():
    user_id = request.form.get('user_id', '')
    file_id = request.form.get('file_id', '')

    if not user_id or not file_id:
        return jsonify({'error': 'missing user_id or file_id'}), 400

    conn = sqlite3.connect('server/database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file_record = c.fetchone()
    conn.close()

    if not file_record:
        return jsonify({'error': 'file not found'}), 404

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found on server'}), 404

    file_md5 = calculate_md5(file_path)

    response = send_file(file_path, as_attachment=True, attachment_filename=f'{file_id}.bin', mimetype='application/octet-stream')
    response.headers['MD5'] = file_md5
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001)
