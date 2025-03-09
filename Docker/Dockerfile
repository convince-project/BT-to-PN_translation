# Use OSRF ROS noetic (Ubuntu 20.04) as the base image
FROM ubuntu:22.04

# Set non-interactive frontend for package installations
ENV DEBIAN_FRONTEND=noninteractive

# Update and install essential packages
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    python3-pip \
    pkg-config \
    libxkbfile-dev \
    libx11-dev \
    libsecret-1-dev \
    git \
    nano \
    python3-tk \
    wget \
    unzip \
    maven \
    npm \
    curl \
    apt-utils \
    && rm -rf /var/lib/apt/lists/*

RUN npm install --global yarn
RUN yarn add keytar

RUN apt remove -y nodejs
ARG version=20
RUN apt update -y && apt install curl unzip -y \
&& curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir './fnm' \
&& cp ./fnm/fnm /usr/bin && fnm install $version

# Set Java environment variables
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:$PATH"

RUN wget https://services.gradle.org/distributions/gradle-6.7.1-bin.zip -P /tmp
RUN yes | unzip -d /opt/gradle -o /tmp/gradle-6.7.1-bin.zip
RUN ln -s /opt/gradle/gradle-6.7.1 /opt/gradle/latest
RUN echo "export GRADLE_HOME=/opt/gradle/latest \nexport PATH=\$PATH:\${GRADLE_HOME}/bin" >> /etc/profile.d/gradle.sh

# Clone your Git repository (replace with your actual repo URL)
WORKDIR /root/
RUN mkdir src
WORKDIR /root/src/
RUN git clone https://github.com/convince-project/BT-to-PN_translation.git
RUN git clone --recurse-submodules https://git-st.inf.tu-dresden.de/dineros/framework/dineros.git
RUN git clone https://git-st.inf.tu-dresden.de/dineros/framework/robotic-sorting.git
RUN git clone https://github.com/verivital/behaverify.git
RUN git clone https://git-st.inf.tu-dresden.de/dineros/framework/pnml-petri-net-editor.git
RUN git clone https://git-st.inf.tu-dresden.de/dineros/framework/sesac-exercise.git

WORKDIR /root/
SHELL ["/bin/bash", "-c"]
RUN echo "source /etc/profile.d/gradle.sh" >> ~/.bashrc
RUN source ~/.bashrc

WORKDIR /root/src/pnml-petri-net-editor
ARG version=20
RUN apt update -y && apt install curl unzip -y \
&& curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir './fnm' \
&& cp ./fnm/fnm /usr/bin && fnm install $version
SHELL ["/bin/bash", "-c"]
RUN source ~/.bashrc
# RUN yarn build

# Set working directory inside the container
# WORKDIR /root/src/BT-to-PN_translation
# Expose any necessary ports (modify as needed)
EXPOSE 11311 8080

# Default command (use Bash for easy manual usage)
CMD ["bash"]
