# Use OSRF ROS noetic (Ubuntu 20.04) as the base image
FROM ubuntu:22.04

# Set non-interactive frontend for package installations
ENV DEBIAN_FRONTEND=noninteractive

# Update and install essential packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    python3-pip \
    libffi8ubuntu1 \
    libncurses-dev \
    libgmp10 \
    libtinfo5 \
    libgmp-dev \
    libgmp3-dev \
    pkg-config \
    libxkbfile-dev \
    libx11-dev \
    libsecret-1-dev \
    libncurses5 \
    git \
    nano \
    wget \
    python3-tk \
    apt-utils \
    && rm -rf /var/lib/apt/lists/*
    
# Clone your Git repository (replace with your actual repo URL)

WORKDIR /root/
RUN git clone https://github.com/convince-project/BT-to-PN_translation.git
RUN git clone https://github.com/verivital/behaverify.git

# Setup environment
# Install Nuxmv
RUN wget https://nuxmv.fbk.eu/theme/download.php?file=nuXmv-2.0.0-linux64.tar.gz -O /tmp/nuXmv-2.0.0-linux64.tar.gz
RUN tar -xzvf /tmp/nuXmv-2.0.0-linux64.tar.gz -C /root/

# Install Behaverify
WORKDIR /root/behaverify
RUN python3 -m pip install -r /root/behaverify/requirements/core.txt
# RUN python3 -m pip install -r /root/BT-to-PN_translation/requirements.txt

# Set working directory inside the container
WORKDIR /root/BT-to-PN_translation
# Expose any necessary ports (modify as needed)
EXPOSE 11311 8080

# Default command (use Bash for easy manual usage)
CMD ["bash"]
