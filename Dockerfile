FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    git \
    gcc-arm-none-eabi \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install pip==22.0.2

RUN useradd -ms /bin/bash easy && \
    mkdir -p /home/easy/.easy_px4 && \

    chown -R easy:easy /home/easy

USER easy
ENV HOME=/home/easy
ENV EASY_PX4_WORK_DIR=/home/easy/.easy_px4
WORKDIR /home/easy

COPY . /easy-px4
WORKDIR ./easy-px4

RUN pip3 install .
