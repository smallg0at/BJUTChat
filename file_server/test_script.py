import requests
import os
import time

# 配置
BASE_URL = 'http://127.0.0.1:5000'
UPLOAD_URL = f'{BASE_URL}/upload'
DOWNLOAD_URL = f'{BASE_URL}/download'
DOWNLOAD_BATCH_URL = f'{BASE_URL}/download_batch'
TEST_FILE_PATH = 'test_upload.txt'
USER_ID = 'test_user'

# 准备测试文件
with open(TEST_FILE_PATH, 'w') as f:
    f.write('This is a test file for upload and download.')

# 测试文件上传
file_ids = []
for i in range(3):
    with open(TEST_FILE_PATH, 'rb') as f:
        files = {'file': f}
        data = {'user_id': USER_ID}
        response = requests.post(UPLOAD_URL, files=files, data=data)

    print('Upload Status Code:', response.status_code)
    print('Upload Response Text:', response.text)

    try:
        upload_response_json = response.json()
        print('Upload Response JSON:', upload_response_json)
        if response.status_code == 200:
            file_ids.append(upload_response_json.get('file_id'))
    except requests.exceptions.JSONDecodeError:
        print('Failed to decode JSON from upload response')

print("Uploaded file IDs:", file_ids)

# 确保所有文件上传成功
if len(file_ids) == 3:
    time.sleep(1)

    # 测试批量文件下载
    download_batch_payload = {'user_id': USER_ID, 'file_ids': file_ids}
    response = requests.post(DOWNLOAD_BATCH_URL, json=download_batch_payload)

    # 打印调试信息
    print('Download Batch Status Code:', response.status_code)
    print('Download Batch Response Headers:', response.headers)
    
    if response.status_code == 200:
        with open('downloaded_files.zip', 'wb') as f:
            f.write(response.content)
        print('Batch file downloaded successfully and saved as downloaded_files.zip')
    else:
        print('Batch file download failed:', response.json())
else:
    print('File upload failed, cannot proceed with batch download')

# 清理测试文件
os.remove(TEST_FILE_PATH)
if os.path.exists('downloaded_files.zip'):
    # os.remove('downloaded_files.zip')
    pass
