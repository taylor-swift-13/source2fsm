import re



# 确保标签内容用大括号包裹
def ensure_brackets(updated_label_content):
    updated_label_content = '{' + updated_label_content + '}'
    return updated_label_content

# 转义源代码
def escape_source_code(source_code):
    # 移除 "else"
    source_code = source_code.replace("else", '')  
    # 转义大于号和小于号
    source_code = source_code.replace('&'  ,'&amp;')
    source_code = source_code.replace('<', '&lt;')
    source_code = source_code.replace('>', '&gt;')
    source_code = source_code.replace('"', '\\"')

    return source_code

def if_condition(source_line):
    
    if 'if' in source_line and '(' in source_line and source_line.split('(')[0].strip()[-1]== 'f':
        return True
    elif 'for'  in source_line and  '(' in source_line and source_line.split('(')[0].strip()[-1]== 'r':
        return True
    elif 'while'  in source_line and  '(' in source_line and source_line.split('(')[0].strip()[-1]== 'e':
        return True

def filter_lines(source_lines):
    source_lines = [line for line in source_lines if line.strip()!='']
    filtered_lines = [line for line in source_lines if not if_condition(line)]
    
    if source_lines and source_lines[-1] != "|{<s0>T|<s1>F}":
        # 过滤掉包含 "if"、"while" 或 "for" 的行
        source_lines = filtered_lines
    return source_lines


# 解析label，去重并处理映射
def parse_label(label_content, ir_to_source_mapping):
    # 去掉首尾的字符
    
    if label_content[0]=='{'and label_content[-1]=='}':
        label_content = label_content.strip()[1:-1]

    ir_lines = label_content.split('\\l')
    source_lines = []
    seen_lines = set()  # 用于去重
    last_ir_line = None
    for ir_line in ir_lines:

        #%5 = call i32 (i8*, ...) @printf(i8* noundef getelementptr inbounds ([6 x i8], [6 x i8]* @.str, i64 0, i64 0))
        ir_line = ir_line.strip()

        if last_ir_line and'...' in last_ir_line and '...' in ir_line :
            ir_line = ir_line.replace('...','')
            new_line =last_ir_line+ir_line
            new_line =new_line.strip()
            if new_line in ir_to_source_mapping:
                source_code = ir_to_source_mapping[new_line]
                escaped_code = escape_source_code(source_code)
                if escaped_code not in seen_lines:
                    source_lines.append(escaped_code)
                    seen_lines.add(escaped_code) 
                
        elif ir_line in ir_to_source_mapping:
            source_code = ir_to_source_mapping[ir_line]
            escaped_code = escape_source_code(source_code)
            if escaped_code not in seen_lines:
                source_lines.append(escaped_code)
                seen_lines.add(escaped_code) 
        else:
            if ir_line not in seen_lines and ir_line:
                if not ('%' in ir_line or ir_line.startswith('...') or ir_line[0].isdigit()):
                    source_lines.append(ir_line)
                    seen_lines.add(ir_line)

        last_ir_line=ir_line

    source_lines = filter_lines(source_lines)


    updated_label_content = '\\l'.join(source_lines)
    #检查 updated_label_content 中 if 语句 后有没有 |
    updated_label_content = ensure_brackets(updated_label_content)

    return updated_label_content


def get_node_name(node):
    # 查找冒号的位置
    colon_index = node.find(':')
    
    # 如果找到冒号，返回冒号前面的部分；否则返回整个字符串
    if colon_index != -1:
        return node[:colon_index]
    else:
        return node
    
# 递归查找直到找到非空label的目标节点
def find_non_empty_target(target_node, node_to_label, edges):

    while target_node in node_to_label and is_empty(node_to_label[target_node]):
        # 找到下一个目标节点
        found_next = False
        # 找到下一个目标节点
        for source, target in edges:
            if get_node_name(source) == get_node_name(target_node):
                target_node = target
                found_next = True
                break
        # 如果没有找到新的目标节点，退出循环
        if not found_next:
            return target_node
        
    return target_node

def is_empty(label):
    # 移除外部的花括号 {}
    content = label.strip()
    
    if content == "{}":
        return True  # 直接空的花括号
    
    # 匹配 "{...|...}" 的模式，捕获左边和右边的内容
    match = re.match(r'^\{\s*(.*?)\s*\|\s*(.*?)\s*\}$', content)
    if match:
        left_part = match.group(1).strip()  # 左侧部分
        return left_part == ""  # 判断左侧部分是否为空，如果为空则是空的
    
    # 移除所有空白字符，检查剩余内容
    content_inside = content.strip('{}').strip()
    return content_inside == ""

# 解析DOT文件，递归更新边直到找到非空label
def parse_dot_file(dot_file_path, ir_to_source_mapping):
    with open(dot_file_path, 'r') as dot_file:
        dot_lines = dot_file.readlines()

    updated_lines = []
    nodes_to_remove = set()  # 存储空label的节点
    edges_to_update = []  # 存储需要更新的边
    node_to_label = {}  # 存储节点与label的对应关系
    all_edges = []  # 存储所有的边

    label_pattern = re.compile(r'label="(.*?)"')
    edge_pattern = re.compile(r'(Node0x[a-fA-F0-9]+(?:\:\w+)?)\s*->\s*(Node0x[a-fA-F0-9]+(?:\:\w+)?)')
    node_pattern = re.compile(r'\bNode0x[a-fA-F0-9]+(:\w+)?\b')

    for line in dot_lines:
        # 处理节点label
        pre_label = ""
        label_match = re.search(label_pattern, line)
        node_match = re.search(node_pattern, line)
        if label_match:
            label_content = label_match.group(1)
            updated_label = parse_label(label_content, ir_to_source_mapping)    

            if not is_empty(pre_label) and not is_empty(updated_label) :
                if updated_label in pre_label:
                    nodes_to_remove.add(node_match.group(0))
           
            if is_empty(updated_label):
                if node_match:
                    nodes_to_remove.add(node_match.group(0))
            else:
                updated_line = line.replace(label_content, updated_label)
                updated_lines.append(updated_line)

            
        
            # 存储节点与label的对应关系
            if node_match:
                node_name = node_match.group(0)
                node_to_label[node_name] = updated_label
        
            pre_label=updated_label

        else:
            updated_lines.append(line)
           
        # 处理边
    for line in dot_lines:    
        edge_match = re.search(edge_pattern, line)
        if edge_match:
            source_node, target_node = edge_match.groups()
            all_edges.append((source_node, target_node))
           
            
            if target_node in nodes_to_remove:  # 如果目标节点是空label的节点
                edges_to_update.append((source_node, target_node))
        
        
    # 递归更新所有指向空label节点的边
    new_edges = []
    for source_node, target_node in edges_to_update:
        new_target_node = find_non_empty_target(target_node, node_to_label, all_edges)
        if new_target_node != target_node:  # 更新边的目标
            new_edges.append(f'        {source_node} -> {new_target_node};\n')

  
    # 创建一个字典映射旧边到新边
    edge_replacement_map = {
        f'{source} -> {target};': new_edge
        for (source, target), new_edge in zip(edges_to_update, new_edges)
    }

    #更新 `updated_lines`，替换旧边为新边
    updated_lines = [
        edge_replacement_map.get(line.strip(), line) 
        for line in updated_lines
    ] 

    # 删除空label的节点行
    updated_lines = [line for line in updated_lines if not any(node in line for node in nodes_to_remove)]

        # 去重并保持顺序
    seen = set()
    unique_lines = []
    for line in updated_lines:
        line_stripped = line.strip()  # 去除前后的空白字符
        if line_stripped not in seen:
            seen.add(line_stripped)
            unique_lines.append(line)

    updated_lines=unique_lines
    

    return updated_lines
