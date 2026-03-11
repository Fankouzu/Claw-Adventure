FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# 装底层的数据库编译依赖
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露 Web 端口和 Telnet 端口
EXPOSE 8000 4000
# 灵魂一步：每次部署自动对比/更新表结构，并带日志前台启动防止容器休眠
CMD ["sh", "-c", "evennia migrate && evennia start -l"]
