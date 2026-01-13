# source2fsm
The tool for generating corresponding finite state machines (FSM) (Control Flow Automata, CFA) from C language code based on LLVM and Graphviz.

基于 LLVM 和 Graphviz  的从 c 语言代码生成对应的有限状态机FSM（控制流自动机，CFA）的工具。

```
输入 (file_name, function_name)
    ↓
[预处理] preProcess.py
    ├─ 读取 .c 文件
    ├─ 读取 .h 文件（如果存在）
    └─ 合并文件内容
    ↓
[生成 LLVM IR] clang
    ├─ 第一次：生成标准 IR (file.ll)
    └─ 第二次：生成带调试信息的 IR (updated.ll)
    ↓
[生成控制流图] opt -dot-cfg
    └─ 输出：.function_name.dot
    ↓
[建立映射] ir2Source.py
    └─ IR 指令 ↔ 源代码行（通过 !dbg 调试信息）
    ↓
[解析 Label] parseLabel.py
    └─ 用源代码替换 DOT 文件中的 IR 指令
    ↓
[分割 Label] divideLabel.py
    └─ 处理多行代码和节点连接
    ↓
[修改 DOT] modifyDot.py
    ├─ 添加节点颜色
    ├─ 处理条件分支
    └─ 优化布局
    ↓
[生成输出]
    ├─ DOT 文件：output/file_function.dot
    └─ PNG 图片：output/file_function.png
    ↓
[清理临时文件]
    └─ 删除 .dot 和 .ll 文件
```


## 依赖

系统版本：

```
ubuntu 22.04
```

python 版本：

```
Python 3.10.12
```

安装依赖：

```
sudo apt-get update
sudo apt-get install llvm clang
pip install graphviz
```

对应版本：

```
Ubuntu clang version 14.0.0-1ubuntu1.1
Ubuntu LLVM version 14.0.0
graphviz version 2.43.0 (0)
```


## 使用

把 file.c 以及所依赖的 .h 文件都放到 input文件夹下，运行：

```
python3 main.py file.c function
```

输入：文件名 file.c 和函数名 function。

输出：对应函数的 fsm，在 output 文件夹中，包含 .dot 和 .png。
