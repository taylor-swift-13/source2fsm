import re

def map_ir_to_source(ir_content, source_code_content):
    # 将源代码按行分割
    source_lines = source_code_content.splitlines()

    # 匹配IR中带有调试信息(!dbg)的指令
    ir_instruction_pattern = re.compile(r'^\s*([^;]+)\s*,\s*!dbg\s*!([0-9]+)')
    # 匹配IR中DILocation的行号信息
    dbg_pattern = re.compile(r'^\s*!([0-9]+)\s*=\s*!DILocation\(line:\s*([0-9]+),')

    # 存储dbg标号对应的行号
    dbg_to_line = {}
    # 存储最终IR指令和源代码的映射
    ir_to_source_mapping = {}

    # 第一步：从IR中解析出dbg标号和对应的行号
    for line in ir_content.splitlines():
        dbg_match = dbg_pattern.match(line)
        if dbg_match:
            dbg_id = dbg_match.group(1)  # dbg标号
            line_number = int(dbg_match.group(2))  # 对应的源码行号
            dbg_to_line[dbg_id] = line_number

    # 第二步：从IR中提取指令并将其与对应的源码行进行匹配
    for line in ir_content.splitlines():
        ir_match = ir_instruction_pattern.match(line)
        if ir_match:
            ir_instruction = ir_match.group(1).strip()  # 提取IR指令
            dbg_id = ir_match.group(2).strip()  # 提取dbg标号
            if dbg_id in dbg_to_line:
                source_line_number = dbg_to_line[dbg_id]  # 获取对应的源码行号
                if 0 < source_line_number <= len(source_lines):
                    # 将IR指令与源码行进行映射
                    ir_to_source_mapping[ir_instruction] = source_lines[source_line_number - 1]  # 源码行数从1开始

    return ir_to_source_mapping


def read_file(file_path):
    """Reads the content of a file and returns it as a string."""
    with open(file_path, 'r') as file:
        return file.read()

def parse_source_code(source_file_path):
    """Reads the source code file and returns its lines."""
    with open(source_file_path, 'r') as file:
        return file.readlines()
