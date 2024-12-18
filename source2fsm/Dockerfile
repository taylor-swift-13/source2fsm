# 使用官方的 Python 3.10 镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /source2fsm

# 将当前目录下的文件复制到 Docker 容器的工作目录
COPY . /source2fsm

# 更新 apt 包列表，并安装 LLVM 14 和其他依赖
RUN apt-get update && \
    # 安装 LLVM 14
    apt-get install -y llvm-14 clang-14 lldb-14 && \
    # 清理缓存
    rm -rf /var/lib/apt/lists/*

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露容器的 5000 端口
EXPOSE 5000

# 设置 Flask 应用的启动命令
CMD ["python3", "app.py"]
