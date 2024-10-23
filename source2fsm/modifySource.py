import re
import os

def modify_statements(file_path):
    # 读取文件
    with open(file_path, 'r') as file:
        code = file.readlines()
    
    file_path_ = f"{file_path.split('.')[0]}_modified.c"
    # 修改 if、while 和 for 语句
    modified_code = []
    for line in code:
        # 修改 if 语句
        modified_line = re.sub(r'^\s*if\s*\((.*?)\)\s*([^{;]*;)', r'if (\1) {\n    \2\n}', line)
        # 修改 while 语句
        modified_line = re.sub(r'^\s*while\s*\((.*?)\)\s*([^{;]*;)', r'while (\1) {\n    \2\n}', modified_line)
        # 修改 for 语句
        modified_line = re.sub(r'^\s*for\s*\((.*?)\)\s*([^{;]*;)', r'for (\1) {\n    \2\n}', modified_line)
        modified_code.append(modified_line)

    # 写回文件
    with open(file_path_, 'w') as file:
        file.writelines(modified_code)

# # 简单调用示例
# if __name__ == "__main__":
#     test_file_path = 'test_source.c'
#     original_code = """\
# #include <stdio.h>

# int main() {
#     int a = 5;
#     if (a > 0) printf("Positive\\n");
#     while (a < 10) printf("Count: %d\\n", a++);
#     for (int i = 0; i < 5; i++) printf("Loop: %d\\n", i);
#     return 0;
# }
# """
#     # 创建测试文件
#     with open(test_file_path, 'w') as test_file:
#         test_file.write(original_code)

#     # 调用修改函数
#     modify_statements(test_file_path)

#     # 打印结果
#     with open(f"{test_file_path}_modified.c", 'r') as modified_file:
#         print(modified_file.read())

    # 清理测试文件
    # os.remove(test_file_path)
    # os.remove(f"{test_file_path.split('.')[0]}_modified.c")
