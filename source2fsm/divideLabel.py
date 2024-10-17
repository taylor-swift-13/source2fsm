import re
             
def nodes_are_connected(lines,node1,node2):
    edge_pattern = re.compile(r'(\w+)(?::(\w+))? -> (\w+);')
    for line in lines:    
        edge_match = re.search(edge_pattern, line)
        if edge_match:
            #print( edge_match.groups())
            source_node, port,target_node = edge_match.groups()
            if (get_node_name(source_node)==node1 and get_node_name(target_node)==node2)or get_node_name(source_node)==node2 and get_node_name(target_node)==node1:
                return True
        else:
            continue
    return False

# '''
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

        
def process_node(data):
    data ='\n'.join(data)
    title= data.split('\n')[0].replace('CFG','FSM')
    # Regular expressions for matching node and edge information
    node_pattern = re.compile(r'(\w+)\s*\[shape=record,color="#\w+", style=filled, fillcolor="#\w+",label="\{(.*?)\}\"];', re.DOTALL)
    edge_pattern = re.compile(r'(\w+)(?::(\w+))? -> (\w+);')

    nodes = {}
    edges = []

    # Extract nodes
    for match in node_pattern.finditer(data):
        node_id, label = match.groups()
        nodes[node_id] = label.strip()

    # Extract edges
    for match in edge_pattern.finditer(data):
        src, port, dst = match.groups()
        edges.append((src, port, dst))

    # Process each node to handle 'if' statements
    new_edges = []
    new_nodes = {}

    # Create a list of items to iterate over
    nodes_items = list(nodes.items())
    for node_id, label in nodes_items:
        
        label_parts = label.split('\\l')
        label_parts = [part.strip() for part in label_parts]
    
        
        # 正则表达式模式，匹配 |{<s0>...|<s1>...|<s2>...|...} 的形式
        cond_pattern = r'^\|\{(<s\d+>[^|]+)(\|<s\d+>[^|]+)*\}$'
        #if label_parts[-1] == '|{<s0>T|<s1>F}' and len(label_parts) >= 2:
        if re.match(cond_pattern, label_parts[-1]) and len(label_parts) >= 2:
            
            cond_part = label_parts[-2] + '\\l' + label_parts[-1]
            pre_cond = '\\l'.join(label_parts[:-2])  # 前面的部分是普通代码

            if pre_cond.strip()==[]:
                new_nodes[node_id] = label
            else:
            # Update node content
                new_nodes[node_id] = pre_cond.strip()
                new_node_id = f'{node_id[:-1]+str(int(node_id[-1])+1%10)}'
                new_nodes[new_node_id] = cond_part.strip()    
            
            new_edges.append((node_id, None, new_node_id))
            # Update edges
            for src, port, dst in edges:
                if src == node_id:
                    new_edges.append((new_node_id, port, dst))  
        else:
            new_nodes[node_id] = label.strip()
            for src, port, dst in edges:
                if src == node_id:
                    new_edges.append((node_id, port, dst))  
        
        

    # Output results
    result = []

    result.append(title)

    for node_id, label in new_nodes.items():
        result.append(f'{node_id} [shape=record,color="#3d50c3ff", style=filled, fillcolor="#f59c7d70",label="{{{label}}}"];')

    for src, port, dst in new_edges:
        if port:
            result.append(f'{src}:{port} -> {dst};')
        else:
            result.append(f'{src} -> {dst};')

    #return '\n'.join(result)
    result.append('}')

    return result



#对 result 去重
def remove_duplicate(result):
    updated_lines = []
    nodes_to_remove = set()  # 存储空label的节点
    edges_to_update = []  # 存储需要更新的边
    node_to_label = {}  # 存储节点与label的对应关系
    all_edges = []  # 存储所有的边

    label_pattern = re.compile(r'label="(.*?)"')
    edge_pattern = re.compile(r'(Node0x[a-fA-F0-9]+(?:\:\w+)?)\s*->\s*(Node0x[a-fA-F0-9]+(?:\:\w+)?)')
    node_pattern = re.compile(r'\bNode0x[a-fA-F0-9]+(:\w+)?\b')


    for line in result:
        # 处理节点label
        label_match = re.search(label_pattern, line)
        node_match = re.search(node_pattern, line)
        if label_match:
            label_content = label_match.group(1)
                        
            if is_empty(label_content):
                if node_match:
                    nodes_to_remove.add(node_match.group(0))
            else:
                updated_lines.append(line)
        
            # 存储节点与label的对应关系
            if node_match:
                node_name = node_match.group(0)
                node_to_label[node_name] = label_content
        
        else:
            updated_lines.append(line)

        
        # 处理边
    for line in result:    
        edge_match = re.search(edge_pattern, line)
        if edge_match:
            source_node, target_node = edge_match.groups()
            all_edges.append((source_node, target_node))
           
            
            if target_node in nodes_to_remove:  # 如果目标节点是空label的节点
                edges_to_update.append((source_node, target_node))
        
        
    #print(nodes_to_remove)

    # 递归更新所有指向空label节点的边
    new_edges = []
    for source_node, target_node in edges_to_update:
        new_target_node = find_non_empty_target(target_node, node_to_label, all_edges)
        if new_target_node != target_node:  # 更新边的目标
            new_edges.append(f'{source_node} -> {new_target_node};\n')

    #print(new_edges)
  
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
    #print(updated_lines)
    
    return '\n'.join(updated_lines)


def divide_label(data):
    # Process data
    result = process_node(data)
    result = remove_duplicate(result)
    return result
