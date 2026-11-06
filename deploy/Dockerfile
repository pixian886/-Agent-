# 应用镜像：FastAPI + Docker CLI（用于调用宿主机的判题容器）
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 安装 Docker CLI；容器通过挂载的 /var/run/docker.sock 调用宿主机 Docker。
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY content ./content
COPY run.py .

RUN mkdir -p /app/data

EXPOSE 8000
CMD ["python", "run.py"]
