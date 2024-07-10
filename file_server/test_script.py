import requests
import os

# 配置
BASE_URL = 'http://127.0.0.1:5000'
UPLOAD_URL = f'{BASE_URL}/upload'
DOWNLOAD_URL = f'{BASE_URL}/download'
TEST_FILE_PATH = 'test_upload.txt'
USER_ID = 'test_user'

# 准备测试文件
with open(TEST_FILE_PATH, 'w') as f:
    f.write('This is a test file for upload and download.')

# 测试文件上传
with open(TEST_FILE_PATH, 'rb') as f:
    files = {'file': f}
    data = {'user_id': USER_ID}
    response = requests.post(UPLOAD_URL, files=files, data=data)

print('Upload Status Code:', response.status_code)
print('Upload Response Text:', response.text)

try:
    upload_response_json = response.json()
    print('Upload Response JSON:', upload_response_json)
except requests.exceptions.JSONDecodeError:
    print('Failed to decode JSON from upload response')

if response.status_code == 200:
    file_id = upload_response_json.get('file_id')

    # 测试文件下载
    params1 = {'user_id': USER_ID, 'file_id': file_id}
    response = requests.get(DOWNLOAD_URL, params=params1)
    
    # 打印调试信息
    print('Download Status Code:', response.status_code)
    print('Download Response Headers:', response.headers)
    
    if response.status_code == 200:
        with open(f'downloaded_{file_id}.bin', 'wb') as f:
            f.write(response.content)
        print(f'File downloaded successfully and saved as downloaded_{file_id}.bin')
    else:
        print('File download failed:', response.json())
else:
    print('File upload failed:', response.text)

# 清理测试文件
os.remove(TEST_FILE_PATH)
if os.path.exists(f'downloaded_{file_id}.bin'):
    os.remove(f'downloaded_{file_id}.bin')
