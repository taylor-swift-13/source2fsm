import pydot 
import os
import re
import html

def unescape_label(source_code):
    source_code = source_code.replace('\\"', '"')
    source_code = source_code.replace('\\|', '|')
    source_code = source_code.replace('&gt;', '>')
    source_code = source_code.replace('&lt;', '<')
    return source_code
    

def render_dot(dot_file):
    # 读取dot文件
    graphs = pydot.graph_from_dot_file(dot_file)
    graph = graphs[0]

    # 用于生成递增的状态名
    state_counter = 1

    switch_flag = False

     # 正则表达式匹配多个 <sX> 分支，例如 |{<s0>T|<s1>F|<s2>U}
    cond_pattern = r'\|\{(<s\d+>[^|]+)(\|<s\d+>[^|]+)*\}'

    # 字典用于存储节点名及其对应的分支
    node_branches_map = {}

    # 遍历所有节点
    for node in graph.get_nodes():
        label = node.get("label")
        node_name = node.get_name()
        match = re.search(cond_pattern, label)

        if label :
            if '|{<s0>T|<s1>F}' in label:
                # 生成递增的状态名，例如 state1, state2, state3 ...
                new_state_name = f"state{state_counter}"
                state_counter += 1

                # 移除 "|{<s0>T|<s1>F}" 和标签中的首尾花括号{}
                label = label.replace('|{<s0>T|<s1>F}', '').replace('{','').replace('}','').replace('\l','').strip('"')

                # 设置新的状态名为节点的 label 和 xlabel
                node.set("label", new_state_name)
                label =  f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD BGCOLOR="lightblue" ALIGN="center">{label}</TD></TR></TABLE>>'
                
                node.set("xlabel",label)
              
                

                # 修改节点形状为圆形，大小，颜色
                node.set_shape("circle")
                node.set_fixedsize("true")
                node.set_width(1.3)
                node.set_height(1.3)
                node.set_style("filled")
                node.set_fillcolor("#ADD8E6")  # 浅蓝色背景

            elif match:
                    
                    switch_flag = True
                    # 生成递增的状态名，例如 state1, state2, state3 ...
                    new_state_name = f"state{state_counter}"
                    state_counter += 1

                    # 提取所有分支的标签和 case 值，只匹配分支格式如 <s0>T
                    branches = re.findall(r'<s(\d+)>([^|}]+)', label)              

                    # 移除所有分支的标签部分
                    label_cleaned = re.sub(cond_pattern, '', label).replace('{', '').replace('}', '').replace('\l', '').strip('"')       
                    switch_key = re.search(r'\(\s*(.*?)\s*\)', label_cleaned).group(1)


                    # 分支的 case 加入 cond
                    branches = [(key, f'{switch_key} : {value}') for key, value in branches]

                    # 将节点名和分支存入字典
                    node_branches_map[node_name] = branches
                   

                    
                    # 设置新的状态名为节点的 label 和 xlabel
                    node.set("label", new_state_name)
                    label_cleaned =  f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD BGCOLOR="lightblue" ALIGN="center">{label_cleaned}</TD></TR></TABLE>>'
                
                    node.set("xlabel", label_cleaned)
                    

                    # 修改节点形状为圆形，大小，颜色
                    node.set_shape("circle")
                    node.set_fixedsize("true")
                    node.set_width(1.3)
                    node.set_height(1.3)
                    node.set_style("filled")
                    node.set_fillcolor("#ADD8E6")  # 浅蓝色背景

 # 遍历所有边
    edges_to_add = []
    edges_to_remove = []
    
    for edge in graph.get_edges():
        source = edge.get_source()
        destination = edge.get_destination()

        

        if switch_flag:
            source_name = source.split(':')[0]
            if source_name in  node_branches_map:
                branches = node_branches_map[source_name]
                for branch_num, case_value in branches:
                    if f":s{branch_num}" in source:
                        source_clean = source.replace(f":s{branch_num}", "")
                        # 检查边是否已存在 
                        case_value = f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD BGCOLOR="grey" ALIGN="center">{case_value}</TD></TR></TABLE>>'
                        new_edge = pydot.Edge(source_clean, destination, label=case_value)   
                        edges_to_add.append(new_edge)
                        edges_to_remove.append(edge)
                        break
        else :     
            new_edge = None
            if ':s0' in source:
                # 修改边为绿色，并移除 :s0
                new_edge = pydot.Edge(source.replace(":s0", ""), destination, color="#00ff00")
            elif ':s1' in source:
                # 修改边为红色，并移除 :s1
                new_edge = pydot.Edge(source.replace(":s1", ""), destination, color="#ff0000")
            if new_edge:
                # 记录要添加和移除的边
                edges_to_add.append(new_edge)
                edges_to_remove.append(edge)
        
       

    # 删除旧边并添加新边
    for edge in edges_to_remove:
        graph.del_edge(edge.get_source(), edge.get_destination())
    
    for new_edge in edges_to_add:
        graph.add_edge(new_edge)

    # 写入修改后的dot文件
    modified_dot_file = '.rendered_' + dot_file
    graph.write(modified_dot_file)

def delete_dot(dot_file):
    # 读取dot文件
    graphs = pydot.graph_from_dot_file(dot_file)
    graph = graphs[0]

    # 存储节点的 xlabel 与节点名的映射
    xlabel_to_node = {}
    edges_to_add = []
    edges_to_remove = []

    # 遍历所有节点，查找 xlabel 相同的节点
    for node in graph.get_nodes():
        xlabel = node.get("xlabel")
        if xlabel:
            if xlabel in xlabel_to_node:
                # 如果找到相同 xlabel 的节点，合并它们
                node_to_merge = xlabel_to_node[xlabel]  # 之前记录的相同 xlabel 的节点
                current_node = node.get_name()
                

                # 处理边，合并两个节点的所有边
                for edge in graph.get_edges():
                    source = edge.get_source()
                    destination = edge.get_destination()

                    if source ==  node_to_merge and destination == current_node:
                        edges_to_remove.append(edge)

                    if source ==  current_node and destination == node_to_merge:
                        edges_to_remove.append(edge)

                    # 如果边指向或来自这两个相同 xlabel 的节点，修改边为指向保留的节点
                    if source ==  current_node:
                        new_edge = pydot.Edge(node_to_merge, destination, color=edge.get("color"))
                        edges_to_add.append(new_edge)
                        edges_to_remove.append(edge)
                    
                    if destination == current_node:
                        edges_to_remove.append(edge)
                        

                # 删除当前节点
                graph.del_node(current_node)

            else:
                # 如果未找到相同 xlabel 的节点，记录当前节点
                xlabel_to_node[xlabel] = node.get_name()

    # 删除旧边并添加新边，避免重复
    for edge in edges_to_remove:
        graph.del_edge(edge.get_source(), edge.get_destination())

     # 去重所有边
    existing_edges = set((edge.get_source(), edge.get_destination()) for edge in graph.get_edges())
    unique_edges_to_add = set((edge.get_source(), edge.get_destination()) for edge in edges_to_add)

    # 仅添加不存在的边
    for source, destination in unique_edges_to_add:
        if (source, destination) not in existing_edges:
            # 查找边的颜色
            color = next(edge.get("color") for edge in edges_to_add if edge.get_source() == source and edge.get_destination() == destination)
            new_edge = pydot.Edge(source, destination, color=color)
            graph.add_edge(new_edge)

  

    # 按递增顺序重新命名节点，只对圆形节点进行操作
    state_counter = 1
    for node in graph.get_nodes():
        if node.get_shape() == 'circle':
            new_state_name = f"state{state_counter}"
            node.set("label", new_state_name)
            state_counter += 1

    # 写入修改后的 dot 文件
    modified_dot_file = '.final.dot'
    graph.write(modified_dot_file)



def modify_dot(dot_file):
    rendered_dot_file = '.rendered_' + dot_file
    render_dot(dot_file)
     # 写入修改后的dot文件
    
    delete_dot(rendered_dot_file)
    if os.path.exists(rendered_dot_file):
        os.remove(rendered_dot_file)  # 删除文件

    