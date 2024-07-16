from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
from hashlib import md5 as _md5

app = Flask(__name__)
app.secret_key = 'your_secret_key'
#CORS(app)

def get_db_connection():
    conn = sqlite3.connect('server/database.db')
    conn.row_factory = sqlite3.Row
    return conn

first_request = True

@app.before_request
def reset_login_info():
    global first_request
    if first_request:
        session.clear()
        first_request = False


@app.route('/')
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return render_template('login.html')
    logged_in = session.get('logged_in', False)
    username = session.get('username', '')
    return render_template('main.html', logged_in=logged_in, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 检查用户凭据（这里是硬编码的用户名和密码检查）
        valid_users = [
            { 'username': 'lty', 'password': '12345678' },
            { 'username': 'lyc', 'password': '87654321' },
            { 'username': 'lcb', 'password': '00000000' },
            { 'username': 'yyb', 'password': '11111111' },
            { 'username': 'flh', 'password': '21933122' },
            { 'username': 'gjy', 'password': '92138121' },
            # 你可以在这里添加更多的硬编码用户
        ]

        is_valid_user = any(user for user in valid_users if user['username'] == username and user['password'] == password)

        if is_valid_user:
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Login failed. Please check your username and password.'}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/signup')
def signup():
    if 'logged_in' in session and session['logged_in']:
        return render_template('signup.html')

@app.route('/announcements')
def email():
    if 'logged_in' in session and session['logged_in']:
        conn = get_db_connection()
        cursor = conn.cursor()
        row = cursor.execute("SELECT title,content,send_time FROM announcements").fetchall()
        conn.close()
        ann_list = []
        for i in row:
            ann_list.append(dict(zip(['title', 'content', 'send_time'], row[i])))
        
        return render_template('announcements.html')

@app.route('/banning_user')
def banning_user():
    if 'logged_in' in session and session['logged_in']:
        return render_template('banning_user.html')

@app.route('/altering_password')
def altering_password():
    if 'logged_in' in session and session['logged_in']:
        return render_template('altering_password.html')

@app.route('/altering_user_info')
def altering_user_info():
    if 'logged_in' in session and session['logged_in']:
        return render_template('altering_user_info.html')

@app.route('/ban_user', methods=['POST'])
def ban_user():
    if 'logged_in' not in session or not session['logged_in']:
        return
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
    if 'logged_in' not in session or not session['logged_in']:
        return
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
    if 'logged_in' not in session or not session['logged_in']:
        return
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
    if 'logged_in' not in session or not session['logged_in']:
        return
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
    if 'logged_in' not in session or not session['logged_in']:
        return
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
