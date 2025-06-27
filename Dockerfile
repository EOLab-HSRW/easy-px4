FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
# required by the Official ubuntu.sh setup script (PX4)
ENV RUNS_IN_DOCKER=true 
ENV EASY_PX4_WORK_DIR=/home/easy
ENV EASY_PX4_CLONE_PX4=false
ENV EASY_PX4_INSTALL_DEPS=false

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

RUN mkdir -p /home/easy/.easy_px4

RUN git clone https://github.com/PX4/PX4-Autopilot --recursive --no-tags ${EASY_PX4_WORK_DIR}/.easy_px4/PX4-Autopilot
WORKDIR ${EASY_PX4_WORK_DIR}/.easy_px4/PX4-Autopilot
RUN chmod +x Tools/setup/ubuntu.sh && Tools/setup/ubuntu.sh

RUN mkdir -p "${EASY_PX4_WORK_DIR}/easy-px4"
COPY . /home/easy/easy-px4
WORKDIR /home/easy/easy-px4

RUN pip3 install . --verbose
