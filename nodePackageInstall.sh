#!/bin/bash

sudo apt-get -y update 
sudo apt-get -y upgrade 
sudo apt-get install -y build-essential libssl-dev
sudo apt-get install -y python python-pip
sudo apt-get install -y libgmp3-dev p7zip-full
sudo apt-get install -y yasm libgmp-dev libpcap-dev libnss3-dev libkrb5-dev pkg-config nvidia-cuda-toolkit nvidia-opencl-dev libopenmpi-dev openmpi-bin
git clone git://github.com/magnumripper/JohnTheRipper -b bleeding-jumbo john
git clone https://github.com/aws/efs-utils
pip install paramiko
pip install scp
cd ~/john/src 
sudo ./configure 
sudo make -s clean 
sudo make -sj4
mkdir efsMount
cd efs-utils
sudo apt-get -y install binutils
./build-deb.sh
sudo apt-get -y install ./build/amazon-efs-utils*deb
sudo apt-get install nfs-common
cd /home/ubuntu/
../run/john --test=0



