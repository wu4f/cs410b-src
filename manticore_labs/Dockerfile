FROM ubuntu:18.04
MAINTAINER blockchain_course

# Users
##############
RUN useradd --create-home --shell /bin/bash auditor

USER root
# install mythril (from https://github.com/ConsenSys/mythril-classic/wiki/Install-from-Pypi-on-Ubuntu)
RUN apt-get update
RUN apt-get install -y python3-pip python3-dev python3-venv z3 git sudo curl software-properties-common golang tmux vim emacs nano

# sudo access
RUN usermod -aG sudo auditor
RUN echo "auditor:manticore" | chpasswd

USER auditor
WORKDIR /home/auditor
# get geth
RUN git clone https://github.com/ethereum/go-ethereum.git
WORKDIR /home/auditor/go-ethereum
RUN git checkout tags/v1.8.22
RUN make
# get the version of solidity for the levels
WORKDIR /home/auditor
RUN mkdir -p ~/solidity_versions/0.4.24/
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.4.24/solc-static-linux > ~/solidity_versions/0.4.24/solc
RUN chmod a+x ~/solidity_versions/0.4.24/solc
RUN git clone https://github.com/trailofbits/manticore.git
WORKDIR /home/auditor/manticore
RUN git checkout tags/0.2.4
RUN git config --global user.email "you@example.com"
RUN git config --global user.name "Your Name"
#ADD manticore_patches/*.patch /home/auditor/manticore/
#RUN git am *.patch
#RUN python3 -m venv ./venv
RUN bash -c "python3 setup.py build"
USER root
RUN bash -c "python3 setup.py install"
USER auditor

# add the solidity examples to the container
ADD ./SI_ctf_levels /home/auditor/SI_ctf_levels
# add information to the home directory
ADD ./README.md /home/auditor/README.md
ADD ./Dockerfile /home/auditor/Dockerfile
# add the level solutions/scaffolding
ADD ./manticore_scripts /home/auditor/manticore_scripts
# add the path to the bashrc:
RUN echo 'export PATH=$PATH:~/solidity_versions/0.4.24/' >> ~/.bashrc

USER root
RUN chown -R auditor:auditor /home/auditor/manticore_scripts
RUN chown -R auditor:auditor /home/auditor/Dockerfile
RUN chown -R auditor:auditor /home/auditor/README.md
RUN chown -R auditor:auditor /home/auditor/SI_ctf_levels

USER auditor
WORKDIR /home/auditor
