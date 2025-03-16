FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y

# Set build-time arguments
ARG VENUE=2025_CAV
ENV USER=BehaVerify_${VENUE}  

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


# Set the working directory
WORKDIR /home/$USER

# Switch to the non-root user
USER $USER

RUN sudo apt-get install wget -y
RUN sudo apt-get install git -y
RUN sudo apt-get install python3 pip python3-venv -y

ADD https://api.github.com/repos/verivital/behaverify/git/refs/heads/main version.json

RUN git clone --filter=blob:none --no-checkout --depth 1 --sparse https://github.com/verivital/behaverify
WORKDIR /home/$USER/behaverify
RUN git sparse-checkout set --no-cone
RUN echo !/* > /home/$USER/behaverify/.git/info/sparse-checkout
RUN echo /REPRODUCIBILITY/$VENUE >> /home/$USER/behaverify/.git/info/sparse-checkout
RUN git checkout

RUN echo $USER > /home/$USER/user.txt
RUN ls /home/$USER/behaverify/

RUN python3 -m venv /home/$USER/python_venvs/behaverify
RUN /home/$USER/python_venvs/behaverify/bin/python3 -m pip install --upgrade pip
RUN /home/$USER/python_venvs/behaverify/bin/python3 -m pip install -r /home/$USER/behaverify/REPRODUCIBILITY/${VENUE}/requirements/core.txt
RUN python3 -m venv /home/$USER/python_venvs/results
RUN /home/$USER/python_venvs/results/bin/python3 -m pip install --upgrade pip
RUN /home/$USER/python_venvs/results/bin/python3 -m pip install -r /home/$USER/behaverify/REPRODUCIBILITY/${VENUE}/requirements/drawing.txt

RUN wget https://nuxmv.fbk.eu/theme/download.php?file=nuXmv-2.0.0-linux64.tar.gz -O /tmp/nuXmv-2.0.0-linux64.tar.gz
RUN tar -xzvf /tmp/nuXmv-2.0.0-linux64.tar.gz -C /home/$USER/behaverify/REPRODUCIBILITY/$VENUE/
RUN ls /home/$USER/behaverify/REPRODUCIBILITY/${VENUE}/nuXmv-2.0.0-Linux/bin

RUN ln -s /home/$USER/behaverify/REPRODUCIBILITY/${VENUE}/nuXmv-2.0.0-Linux/bin/nuXmv /home/$USER/behaverify/REPRODUCIBILITY/${VENUE}/nuXmv

WORKDIR /home/$USER