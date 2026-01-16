
import pydot 
import os
import re
from enum import Enum

class Color(Enum):
    NODE_DEFAULT = '#F5F5F5'      # 浅灰白
    NODE_CONDITION = '#E8F4FD'    # 淡蓝
    NODE_LOOP = '#FFF9E6'         # 淡黄
    NODE_SWITCH = '#F0F0F0'       # 中灰
    EDGE_TRUE = '#34C759'         # 柔和绿
    EDGE_FALSE = '#FF6B6B'        # 柔和红
    EDGE_DEFAULT = '#BDBDBD'      # 中灰
    BORDER = '#E0E0E0'            # 边框灰
    TEXT = '#333333'              # 深灰文字


def undepulicate_label(label):
    segments = label.split(')')
    processed_segments = [segment.strip() for segment in segments]
    label = ')'.join(processed_segments)

    segments = label.split(';')
    processed_segments = [segment.strip() for segment in segments]
    label = ';'.join(processed_segments)
    
    return label


def render_dot(dot_file):
    graphs = pydot.graph_from_dot_file(dot_file)
    graph = graphs[0]

    # 全局图样式 - 极简设置
    graph.set_bgcolor('white')
    graph.set_pad('0.5')
    graph.set_nodesep('0.6')
    graph.set_ranksep('0.8')

    state_counter = 1
    switch_flag = False
    cond_pattern = r'\|\{(<s\d+>[^|]+)(\|<s\d+>[^|]+)*\}'
    node_branches_map = {}

    for node in graph.get_nodes():
        label = node.get("label")
        node_name = node.get_name()
        match = re.search(cond_pattern, label)

        if label:
            if '|{<s0>T|<s1>F}' in label:
                new_state_name = f"state{state_counter}"
                state_counter += 1

                label = label.replace('|{<s0>T|<s1>F}', '').replace('{','').replace('}','').replace('\l','').strip('"')
                
                node.set("label", new_state_name)
                
                # 极简标签样式
                is_loop = "while" in label or "for" in label
                bg_color = Color.NODE_LOOP.value if is_loop else Color.NODE_CONDITION.value
                label = f'<<FONT FACE="Helvetica" POINT-SIZE="11" COLOR="{Color.TEXT.value}">{label}</FONT>>'
                node.set("xlabel", label)

                # 极简节点样式
                node.set_shape("circle")
                node.set_fixedsize("true")
                node.set_width(1.0)
                node.set_height(1.0)
                node.set_style("filled")
                node.set_fillcolor(bg_color)
                node.set_color(Color.BORDER.value)
                node.set_fontname("Helvetica")
                node.set_fontsize("10")
                node.set_fontcolor(Color.TEXT.value)

            elif match:
                switch_flag = True
                new_state_name = f"state{state_counter}"
                state_counter += 1

                branches = re.findall(r'<s(\d+)>([^|}]+)', label)
                label_cleaned = re.sub(cond_pattern, '', label).replace('{', '').replace('}', '').replace('\l', '').strip('"')
                switch_key = re.search(r'\(\s*(.*?)\s*\)', label_cleaned).group(1)

                branches = [(key, f'{switch_key} : {value}') for key, value in branches]
                node_branches_map[node_name] = branches

                node.set("label", new_state_name)
                label_cleaned = f'<<FONT FACE="Helvetica" POINT-SIZE="11" COLOR="{Color.TEXT.value}">{label_cleaned}</FONT>>'
                node.set("xlabel", label_cleaned)

                node.set_shape("circle")
                node.set_fixedsize("true")
                node.set_width(1.0)
                node.set_height(1.0)
                node.set_style("filled")
                node.set_fillcolor(Color.NODE_SWITCH.value)
                node.set_color(Color.BORDER.value)
                node.set_fontname("Helvetica")
                node.set_fontsize("10")
                node.set_fontcolor(Color.TEXT.value)

            else:
                node.set_color(Color.BORDER.value)
                node.set_fillcolor(Color.NODE_DEFAULT.value)
                node.set_style("filled")
                node.set_fontname("Helvetica")
                node.set_fontsize("10")
                node.set_fontcolor(Color.TEXT.value)

    edges_to_add = []
    edges_to_remove = []
    
    for edge in graph.get_edges():
        source = edge.get_source()
        destination = edge.get_destination()
        source_name = source.split(':')[0]

        if switch_flag and source_name in node_branches_map:
            branches = node_branches_map[source_name]
            for branch_num, case_value in branches:
                if f":s{branch_num}" in source:
                    source_clean = source.replace(f":s{branch_num}", "")
                    case_value = f'<<FONT FACE="Helvetica" POINT-SIZE="9" COLOR="{Color.TEXT.value}">{case_value}</FONT>>'
                    new_edge = pydot.Edge(source_clean, destination, label=case_value)
                    edges_to_add.append(new_edge)
                    edges_to_remove.append(edge)
                    break
        else:
            new_edge = None
            if ':s0' in source:
                new_edge = pydot.Edge(source.replace(":s0", ""), destination, color=Color.EDGE_TRUE.value)
            elif ':s1' in source:
                new_edge = pydot.Edge(source.replace(":s1", ""), destination, color=Color.EDGE_FALSE.value)
            if new_edge:
                edges_to_add.append(new_edge)
                edges_to_remove.append(edge)

    for edge in edges_to_remove:
        graph.del_edge(edge.get_source(), edge.get_destination())
    
    for new_edge in edges_to_add:
        graph.add_edge(new_edge)

    modified_dot_file = '.rendered_' + dot_file
    graph.write(modified_dot_file)


def delete_dot(dot_file):
    graphs = pydot.graph_from_dot_file(dot_file)
    graph = graphs[0]

    xlabel_to_node = {}
    edges_to_add = []
    edges_to_remove = []

    for node in graph.get_nodes():
        xlabel = node.get("xlabel")
        if xlabel:
            if xlabel in xlabel_to_node:
                node_to_merge = xlabel_to_node[xlabel]
                current_node = node.get_name()

                for edge in graph.get_edges():
                    source = edge.get_source()
                    destination = edge.get_destination()

                    if source == node_to_merge and destination == current_node:
                        edges_to_remove.append(edge)

                    if source == current_node and destination == node_to_merge:
                        edges_to_remove.append(edge)

                    if source == current_node:
                        new_edge = pydot.Edge(node_to_merge, destination, color=edge.get("color"))
                        edges_to_add.append(new_edge)
                        edges_to_remove.append(edge)
                    
                    if destination == current_node:
                        edges_to_remove.append(edge)

                graph.del_node(current_node)
            else:
                xlabel_to_node[xlabel] = node.get_name()

    for edge in edges_to_remove:
        graph.del_edge(edge.get_source(), edge.get_destination())

    existing_edges = set((edge.get_source(), edge.get_destination()) for edge in graph.get_edges())
    unique_edges_to_add = set((edge.get_source(), edge.get_destination()) for edge in edges_to_add)

    for source, destination in unique_edges_to_add:
        if (source, destination) not in existing_edges:
            color = next(edge.get("color") for edge in edges_to_add if edge.get_source() == source and edge.get_destination() == destination)
            new_edge = pydot.Edge(source, destination, color=color)
            graph.add_edge(new_edge)

    state_counter = 1
    for node in graph.get_nodes():
        if node.get_shape() == 'circle':
            new_state_name = f"state{state_counter}"
            node.set("label", new_state_name)
            state_counter += 1

    defined_nodes = {node.get_name() for node in graph.get_nodes()}
   
    for edge in graph.get_edges():
        source = edge.get_source()
        target = edge.get_destination()
        if target not in defined_nodes:
            graph.del_edge(source, target)
     
    for node in graph.get_nodes():
        label = node.get("label")
        xlabel = node.get("xlabel")
        label = undepulicate_label(label)

        if xlabel is not None: 
            xlabel = undepulicate_label(xlabel)
            node.set("xlabel", xlabel)
        
        node.set("label", label)
  
    # 极简边样式
    for edge in graph.get_edges():
        edge.set_penwidth(1.5)
        edge.set_arrowsize(0.7)
        if edge.get_color() is None:
            edge.set_color(Color.EDGE_DEFAULT.value)

    modified_dot_file = '.final.dot'
    graph.write(modified_dot_file)


def modify_dot(dot_file):
    rendered_dot_file = '.rendered_' + dot_file
    render_dot(dot_file)
    delete_dot(rendered_dot_file)
    
    if os.path.exists(rendered_dot_file):
        os.remove(rendered_dot_file) 
