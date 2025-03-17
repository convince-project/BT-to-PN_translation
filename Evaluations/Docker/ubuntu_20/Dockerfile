# Use the official Ubuntu 20.04 base image
FROM ubuntu:20.04

# Set environment variables to non-interactive to prevent prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_VERSION=11
ENV USER=ubuntu_usr 

# Ensure user and group IDs are defined
ARG UID=22237
ARG GID=22237

# Create a non-root user
RUN groupadd -g $GID "$USER" \
    && useradd -u $UID -g $GID -m -s /bin/bash "$USER"

# Give sudo privileges to the non-root user
RUN apt-get update && apt-get install -y sudo \
    && echo "$USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER \
    && chmod 0440 /etc/sudoers.d/$USER

# Verify user creation
RUN cat /etc/passwd | grep "$USER"

WORKDIR /home/$USER/

# Update the package list and install required tools
RUN apt-get update && apt-get install -y \
    openjdk-$JAVA_VERSION-jdk \
    wget \
    unzip \
    maven \
    npm \
    curl \
    python3-rosdep \
    python3-rosinstall \
    python3-rosinstall-generator \
    python3-wstool \
    build-essential \
    locales \
    git \
    nano \
    gnupg2 \
    lsb-release \
    && locale-gen en_US.UTF-8

# Set locale
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Add the ROS repository
RUN curl -sSL http://packages.ros.org/ros.key | apt-key add - && \
    sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

RUN git clone --recurse-submodules https://git-st.inf.tu-dresden.de/dineros/framework/dineros.git

# # Initialize ROS environment
# RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc

# Install Tina
RUN wget https://projects.laas.fr/tina/binaries/tina-3.7.0-amd64-linux.tgz -O /tmp/tina-3.7.0-amd64-linux.tgz
RUN mkdir -p /home/$USER/tina-3.7.0 && tar -xzvf /tmp/tina-3.7.0-amd64-linux.tgz -C /home/$USER/tina-3.7.0 --strip-components=1

ENV JAVA_VERSION=11
ENV GRADLE_VERSION=6.7.1

# Set Java environment variables
ENV JAVA_HOME="/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install gradle
RUN wget https://services.gradle.org/distributions/gradle-$GRADLE_VERSION-bin.zip -P /tmp
RUN yes | unzip -d /opt/gradle -o /tmp/gradle-$GRADLE_VERSION-bin.zip
RUN ln -s /opt/gradle/gradle-$GRADLE_VERSION /opt/gradle/latest
RUN echo "export GRADLE_HOME=/opt/gradle/latest \nexport PATH=\$PATH:\${GRADLE_HOME}/bin" >> /etc/profile.d/gradle.sh


WORKDIR /home/$USER/dineros/pnml-relast-tools/pnml-relast-engine
RUN ./gradlew fatJar
WORKDIR /home/$USER/dineros/pnml-relast-tools/pnml-relast-splitter
RUN ./gradlew fatJar
WORKDIR /home/$USER/dineros/pnml-relast-tools/pnml-relast-flattener
RUN ./gradlew fatJar

WORKDIR /home/$USER/
RUN chmod a+w /home/$USER/
RUN mkdir inputs
RUN mkdir inputs/PNMLs
RUN mkdir inputs/GRPNs


# Expose ROS default ports
EXPOSE 11311

# Set the entrypoint
ENTRYPOINT ["bash"]
