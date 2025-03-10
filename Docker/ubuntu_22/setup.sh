#!/bin/bash -i

# Install Nuxmv
wget https://nuxmv.fbk.eu/theme/download.php?file=nuXmv-2.0.0-linux64.tar.gz -O /tmp/nuXmv-2.0.0-linux64.tar.gz
tar -xzvf /tmp/nuXmv-2.0.0-linux64.tar.gz -C /root/src/

# Install the correct version of Nodejs
version=20
apt update -y && apt install curl unzip -y \
&& curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir './fnm' \
&& cp ./fnm/fnm /usr/bin && fnm install $version
source /root/.bashrc

# Setup the pnml editor
cd /root/src/pnml-petri-net-editor
yarn build
