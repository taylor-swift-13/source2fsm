from flask import Flask, request, jsonify
import requests
import json
import re
import subprocess

app = Flask(__name__)

download_url = ""
upload_url = ""

def get_first_function_name(c_code):
    # 正则表达式，匹配C语言函数定义（包括返回类型和函数名）
    pattern = r'\b[\w\*]+\s+(\w+)\s*\('  # 匹配类似 "int main(" 或 "void foo(" 的函数定义
    
    # 使用 re.search 查找第一个匹配项
    match = re.search(pattern, c_code)
    
    if match:
        return match.group(1)  # 返回第一个匹配的函数名
    else:
        return None  # 没有找到函数

def read_c_file(file_path):
    # 打开并读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            c_code = file.read()
        return c_code
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def download_file(url, save_path, data):
    try:
        # 使用 POST 请求发送数据
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        
        # 检查请求是否成功
        if response.status_code == 200:
            # 将返回的文件内容写入本地文件
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"File successfully downloaded to {save_path}")
            return True
        else:
            print(f"Failed to download file from {url}, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error occurred while downloading file: {e}")
        return False

# 上传文件到服务器 B
def upload_file(file_path, upload_url):
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(upload_url, files=files)
            return response
    except Exception as e:
        print(f"Error occurred while uploading file to Server B: {e}")
        return None

@app.route('/process_files', methods=['POST'])
def process_files():
    data = request.json

    file_c = { "filePath": data.get('fileC')}
    file_h = { "filePath": data.get('fileH') }

    print(file_c)

    if not file_c or not file_h:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # 下载文件
        file_1_path = "input/code.c"
        file_2_path = "input/code.h"

        if not download_file(download_url, file_1_path,file_c) or not download_file(download_url,file_2_path, file_h):
            return jsonify({"error": "Failed to download files from provided URLs"}), 500
        
        c_code = read_c_file(file_1_path)
        func_name = get_first_function_name(c_code)

        print(func_name)

        subprocess.run(['python3', 'main.py', 'code.c', func_name], capture_output=True, text=True)
        
        output_file_path = f"output/code_{func_name}.png"
        
        response = upload_file(output_file_path, upload_url)

        if response and response.status_code == 200:
            upload_file_path =response.json().get('fileMsg', {}).get('filePath')
            return jsonify({"filePath": upload_file_path}), 200
            
        else:
            return jsonify({"error": "Failed to upload the file to Server B"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the files"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
