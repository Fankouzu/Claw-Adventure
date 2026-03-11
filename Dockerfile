FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 安装数据库编译依赖
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 设置启动脚本权限
RUN chmod +x /app/server/start.sh

# 暴露 Web 端口和 Telnet 端口
EXPOSE 8000 4000

# 启动服务（自动 migrate + 创建 superuser + 启动）
CMD ["/app/server/start.sh"]