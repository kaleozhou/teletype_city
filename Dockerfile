# 使用Python 3.9官方镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV GAME_PORT=2323

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    telnet \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY *.py .
COPY world/ ./world/
COPY systems/ ./systems/
COPY persist/ ./persist/
COPY data/ ./data/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p logs backups

# 创建非root用户
RUN useradd -m -u 1000 gameuser && chown -R gameuser:gameuser /app
USER gameuser

# 暴露游戏端口
EXPOSE 2323

# 启动命令
CMD ["python3", "start_server.py"]
