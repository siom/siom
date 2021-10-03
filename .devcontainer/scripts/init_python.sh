#!/bin/bash
set -e

curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/4164fced49af78c6275cb436c64369eb39c6acb1/bin/pyenv-installer | bash
eval "$(pyenv init -)"
pyenv install 2.7.12

pyenv global 2.7.12
sudo curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py
python get-pip.py
python -m pip install virtualenv --upgrade
sudo rm get-pip.py

echo 'eval "$(pyenv init -)"' >> /home/vscode/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> /home/vscode/.bashrc

eval "$(pyenv virtualenv-init -)"
pyenv virtualenv 2.7.12 siom_venv
pyenv global siom_venv
