FROM ubuntu:22.04

ENV EASY_PX4_WORK_DIR=/home/easy

RUN apt-get update && apt-get install -y \
    git \
    gcc-arm-none-eabi \
    cmake \
    build-essential \
    pkg-config \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install pip==22.0.2

CMD mkdir -p "${EASY_PX4_WORK_DIR}/easy-px4"
COPY . /home/easy/easy-px4
WORKDIR /home/easy/easy-px4

RUN pip3 install .
