# source2fsm
The tool for generating corresponding finite state machines (FSM) (Control Flow Automata, CFA) from C language code based on LLVM and Graphviz.

基于 LLVM 和 Graphviz  的从 c 语言代码生成对应的有限状态机FSM（控制流自动机，CFA）的工具。

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
pip install -r requirements.txt
```

对应版本：

```
Ubuntu clang version 14.0.0-1ubuntu1.1
Ubuntu LLVM version 14.0.0
pydot==3.0.1
```


## 使用

把 file.c 以及所依赖的 .h 文件都放到 input文件夹下，运行：

```
python3 main.py file.c function
```

输入：文件名 file.c 和函数名 function。

输出：对应函数的 fsm，在 output 文件夹中，包含 .dot 和 .png。
