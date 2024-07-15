from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
from hashlib import md5 as _md5

app = Flask(__name__)
# CORS(app)

def get_db_connection():
    conn = sqlite3.connect('server/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/email')
def email():
    return render_template('email.html')

@app.route('/banning_user')
def banning_user():
    return render_template('banning_user.html')

@app.route('/altering_password')
def altering_password():
    return render_template('altering_password.html')

@app.route('/altering_user_info')
def altering_user_info():
    return render_template('altering_user_info.html')

@app.route('/ban_user', methods=['POST'])
def ban_user():
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'User ID is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_banned = 1 WHERE id = ?", (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'User ID not found'}), 404

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    finally:
        conn.close()

def md5(text):
    """计算md5值"""
    m = _md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

@app.route('/change_password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        school_id = data.get('school_id')
        new_password = data.get('newPassword')

        if not school_id or not new_password:
            return jsonify({'success': False, 'message': 'Username and new password are required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE school_id = ?", (md5(new_password), school_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Username not found'}), 404

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    finally:
        conn.close()

@app.route('/update_user_info', methods=['POST'])
def update_user_info():
    try:
        data = request.get_json()
        username = data.get('username')
        school_id = data.get('school_id')
        nickname = data.get('nickname')
        role = data.get('role')

        if not username or not school_id or not nickname or not role:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET school_id = ?, nickname = ?, role = ?
            WHERE username = ?
        """, (school_id, nickname, role, username))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Username not found'}), 404

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    finally:
        conn.close()

@app.route('/create_announcement', methods=['POST'])
def create_announcement():
    try:
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'success': False, 'message': 'Content is required'}), 400

        send_time = datetime.now()
        expiry_time = send_time + timedelta(days=1)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO announcements (content, send_time, expiry_time, visible_to_students, visible_to_teachers)
            VALUES (?, ?, ?, 1, 1)
        """, (content, send_time, expiry_time))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

@app.route('/delete_all_announcements', methods=['DELETE'])
def delete_all_announcements():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM announcements")
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
