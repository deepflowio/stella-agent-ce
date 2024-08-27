# 构建层
FROM python:3.8-slim-buster AS builder
RUN apt-get update && \
    apt-get install --no-install-suggests \
    --no-install-recommends --yes \
    python3-venv \
    gcc \
    libpython3-dev \
    libpq-dev \
    default-libmysqlclient-dev \
    make \
    && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip --trusted-host mirrors.aliyun.com --index-url https://mirrors.aliyun.com/pypi/simple

# Base 构建层
FROM builder AS builder-venv-base
RUN /venv/bin/pip install cffi --trusted-host mirrors.aliyun.com --index-url https://mirrors.aliyun.com/pypi/simple/

# 自定义构建层
FROM builder-venv-base AS builder-venv-custom
COPY requirements3.txt /requirements3.txt
RUN /venv/bin/pip install --disable-pip-version-check \
     	 --no-cache-dir \
         --trusted-host mirrors.aliyun.com \
         --index-url https://mirrors.aliyun.com/pypi/simple/ \
         -r /requirements3.txt

FROM python:3.8-slim-buster AS runner

WORKDIR /df-llm-agent/

RUN apt-get update && apt-get install --no-install-suggests --no-install-recommends --yes gcc libpython3-dev
COPY --from=builder-venv-custom /usr/lib/*-linux-gnu/*.so* /usr/lib/x86_64-linux-gnu/
RUN mkdir /usr/lib/x86_64-linux-gnu/mariadb19
COPY --from=builder-venv-custom /usr/lib/*-linux-gnu/mariadb19/ /usr/lib/x86_64-linux-gnu/mariadb19/
COPY --from=builder-venv-custom /venv /venv

# Copy code
## 复制代码
COPY ./etc/df-llm-agent.yaml /etc/web/
COPY ./df-llm-agent /df-llm-agent/

# 设置root密码
RUN echo 'root:deepflow' | chpasswd

# 创建用户 deepflow，ID 为 1000
RUN useradd -u 1000 -m deepflow -s /bin/bash

RUN chmod +x /df-llm-agent/py2c.sh  && \
    chown -R deepflow:deepflow /df-llm-agent && \
    chown -R deepflow:deepflow /venv

RUN /df-llm-agent/py2c.sh

RUN ls -la /df-llm-agent

## dockerfile里的db_version 和issu里最大版本的x.x.x.x.sql 一致
ENV DB_VERSION=1.0.0.0

## Run
CMD /venv/bin/python3 -u /df-llm-agent/app.py

