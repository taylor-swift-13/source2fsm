import argparse
import os
import subprocess
import glob
from ir2Source import map_ir_to_source
from parseLabel import parse_dot_file
from divideLabel import divide_label
from modifiedDot import modify_dot
# from preProcess import pre_process
from preProcess import pre_process_

def read_file(file_path):
    """Reads the content of a file and returns it as a string."""
    with open(file_path, 'r') as file:
        return file.read()

def parse_source_code(source_file_path):
    """Reads the source code file and returns its lines."""
    with open(source_file_path, 'r') as file:
        return file.readlines()

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def remove_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)  # 删除文件

def rename_file(old_file_name,new_file_name):
    if os.path.exists(old_file_name):
        os.rename(old_file_name, new_file_name)  # 重命名文件

def main():
    # 创建解析器
    parser = argparse.ArgumentParser(description="Read file_name and function_name from command-line arguments.")
    
    # 添加两个必需的参数 file_name 和 function_name
    parser.add_argument('file_name', type=str, help="The name of the file")
    parser.add_argument('function_name', type=str, help="The name of the function")

    # 解析参数
    args = parser.parse_args()

    file_name = args.file_name

    #file_path= pre_process(file_name)
    file_path= pre_process_(file_name)
    #print(file_path)
    function_name =args.function_name

    # 输出参数
    print("File name:", args.file_name)
    print("Function name:", args.function_name)

    dot_file_path = f'.{function_name}.dot'
    output_file_path = '.output.dot'
    ir_file_path = f"{file_name.split('.', 1)[0]}.ll"
    modified_file_path = '.final.dot'

    # 输出文件夹
    output_folder = "output"

    # 创建 output 文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 构建文件路径
    final_file_path = os.path.join(output_folder, f".{file_name.split('.', 1)[0]}_{function_name}.dot")
    png_file_path = os.path.join(output_folder, f"{file_name.split('.', 1)[0]}_{function_name}.png")


    # 使用 subprocess 运行 clang 命令
    command_1 = ["clang", "-S", "-emit-llvm", file_path, "-o", ir_file_path ]

    # 使用 subprocess 运行 clang 命令
    command_2 = ["clang", "-O0", "-g", "-S", "-emit-llvm", file_path, "-o", 'updated.ll']

    
    command_3 = ["opt","-dot-cfg", "-disable-output","-enable-new-pm=0",ir_file_path ]

    
    # 执行命令
    try:
        subprocess.run(command_1, check=True)
        print(f"successfully generated IR: {ir_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"fail in generating IR: {e}")
    
       # 执行命令
    try:
        subprocess.run(command_2, check=True)
        print(f"successfully generated dbg IR: updated.ll")
    except subprocess.CalledProcessError as e:
        print(f"fail in generating dbg IR: {e}")

        # 调用命令
    try:
        subprocess.run(command_3, check=True)
        print(f"successfully generated dot: {dot_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"fail in generating dot: {e}")


    ir_content = read_file("updated.ll")
    source_code_content = read_file(file_path)
    ir_to_source_mapping = map_ir_to_source(ir_content, source_code_content)

    # 解析.dot文件并更新label内容
    updated_dot_lines = parse_dot_file(dot_file_path, ir_to_source_mapping)

    output_dot_lines =divide_label(updated_dot_lines)

    write_file(output_file_path, output_dot_lines)

    modify_dot(output_file_path)

    rename_file(modified_file_path,final_file_path)
    
    print(f"successfully generated dot: {final_file_path}")

    # 构造命令
    command_4 = ["dot", "-Tpng", f"-o{png_file_path}", final_file_path]

    try:
        subprocess.run(command_4, check=True)
        print(f"successfully generated png: {png_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"fail in generating png: {e}")
    
    # 获取当前目录下所有 .dot 文件
    dot_files = glob.glob(".*.dot")
    

    # 删除每个 .dot 文件
    for dot_file in dot_files:
        os.remove(dot_file)
    
      # 获取当前目录下所有 .dot 文件
    ll_files = glob.glob("*.ll")
    

    # 删除每个 .dot 文件
    for ll_file in ll_files:
        os.remove(ll_file)
    

if __name__ == "__main__":
         main()

