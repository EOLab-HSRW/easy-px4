FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    git \
    gcc-arm-none-eabi \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install pip==22.0.2

COPY . /easy-px4
WORKDIR /easy-px4

RUN pip3 install .
