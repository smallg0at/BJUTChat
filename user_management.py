import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('server/database.db')
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route('/change_password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        username = data.get('username')
        new_password = data.get('newPassword')

        if not username or not new_password:
            return jsonify({'success': False, 'message': 'Username and new password are required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=23338)
