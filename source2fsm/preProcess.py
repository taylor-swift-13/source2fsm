import os
import re

def remove_include_statements(content, file_name):
    # 使用正则表达式删除包含特定文件名的 #include 语句，前面的路径无关
    pattern = r'#include\s*["\'].*?{}["\']'.format(re.escape(file_name))
    return re.sub(pattern, '', content)


def pre_process(file_name):
    # 指定输入目录和文件名
    input_dir = "input"

    c_file_name = file_name
    ip_file_name = "IP.h"
    header_file_name = c_file_name[:-1]+'h'

    file_path = os.path.join(input_dir, c_file_name)
    ip_header_path = os.path.join(input_dir, ip_file_name)
    header_file_path =os.path.join(input_dir,header_file_name)

    # 确保文件路径是 .c 文件
    if not os.path.isfile(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return

    # 拼接输出文件名
    base_name = os.path.splitext(file_path)[0]
    output_file_path = f"{base_name}_.c"

    try:
        # 读取 .c 文件内容
        with open(file_path, 'r') as c_file:
            c_content = c_file.read()

        # 读取同名 .h 文件内容
        h_content = ""
        if os.path.isfile(header_file_path):
            with open(header_file_path, 'r') as h_file:
                h_content = h_file.read()
        else:
            print(f"Warning: Header file {header_file_path} does not exist.")

        # 读取 IP.h 文件内容
        ip_content = ""
        if os.path.isfile(ip_header_path):
            with open(ip_header_path, 'r') as ip_file:
                ip_content = ip_file.read()
        else:
            print(f"Warning: IP.h file does not exist.")

        # 删除对应的 #include 语句
        
        c_content = remove_include_statements(c_content, header_file_name)
        
        h_content = remove_include_statements(h_content, ip_file_name)

        # 输出拼接后的内容到 file_.c，.h 文件在前
        with open(output_file_path, 'w') as output_file:
            output_file.write(ip_content + "\n" + h_content + "\n" + c_content)

        print(f"Preprocessed file written to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    return output_file_path


def pre_process_(file_name):
    # 指定输入目录和文件名
    input_dir = "input"

    c_file_name = file_name
    file_path = os.path.join(input_dir, c_file_name)

    # 确保文件路径是 .c 文件
    if not os.path.isfile(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return
    
    return file_path









