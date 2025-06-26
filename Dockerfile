FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    git \
    gcc-arm-none-eabi \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install pip==22.0.2

RUN useradd -ms /bin/bash easy && \
    chown -R easy:easy /home/easy

USER easy
ENV HOME=/home/easy
ENV EASY_PX4_WORK_DIR=/home/easy
WORKDIR /home/easy

COPY . /home/easy/easy-px4
RUN chown -R easy:easy /home/easy/easy-px4 # source folder
RUN chown -R easy:easy /home/easy/.easy_px4 # working folder
WORKDIR /home/easy/easy-px4

RUN pip3 install .
