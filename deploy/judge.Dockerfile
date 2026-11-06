# 判题镜像：只包含 Python 标准库与 requests，供站内编程题使用
FROM python:3.12-slim

RUN pip install --no-cache-dir requests==2.32.3
