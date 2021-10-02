# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.194.0/containers/ubuntu/.devcontainer/base.Dockerfile

FROM mcr.microsoft.com/vscode/devcontainers/base:0.202.0-ubuntu-18.04

RUN apt-get update && \
    apt-get install -y make build-essential libssl1.0-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev

# Give the vscode user access to the /home/www directory
RUN mkdir /home/www && chown -R vscode:vscode /home/www

USER vscode
ENV HOME="/home/vscode"
ENV PYENV_ROOT="$HOME/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

RUN curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/4164fced49af78c6275cb436c64369eb39c6acb1/bin/pyenv-installer | bash && \
    eval "$(pyenv init -)" && \
    pyenv install 2.7.12
    
# This lib is needed for MySQL-python, but for some reason it won't install together with all other libs defined above.
RUN sudo apt-get install -y  default-libmysqlclient-dev

# Also install a mysql client for easier inspection of the DB
RUN sudo apt-get install -y mysql-client-core-5.7

RUN sudo apt-get install -y texlive dvipng

RUN pyenv global 2.7.12 && \
    sudo curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py && \
    python get-pip.py && \
    python -m pip install virtualenv --upgrade && \
    sudo rm get-pip.py

RUN echo 'eval "$(pyenv init -)"' >> /home/vscode/.bashrc && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> /home/vscode/.bashrc

RUN eval "$(pyenv virtualenv-init -)" && \
    pyenv virtualenv 2.7.12 siom_venv && \
    pyenv global siom_venv

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    sudo rm /tmp/requirements.txt

RUN mkdir -p /home/www/siom/logs && \
    ln -sf /workspace/ /home/www/siom/web
COPY ./static/ /home/www/siom/static

# set up isolate
RUN sudo apt-get install -y libcap-dev
RUN mkdir -p /home/www/siom/sandbox && \
    git clone https://github.com/ioi/isolate.git /home/www/siom/sandbox/isolate && \
    cd /home/www/siom/sandbox/isolate && \
    git checkout v1.4.1 && \
    make isolate && \
    sudo cp isolate isolate-check-environment /usr/local/bin && \
    sudo chmod 4755 /usr/local/bin/isolate

COPY .devcontainer/isolate_config.txt /usr/local/etc/isolate 

USER vscode

# create link in the sandbox folder
RUN ln -s /home/www/siom/grader/tasks /home/www/siom/sandbox/tasks && \
    ln -s /home/www/siom/web/grader/checker.py /home/www/siom/sandbox/checker.py

# add some sample test cases (will move to a different place later)
RUN mkdir -p /home/www/siom/grader/tasks/pomidorai_jau && \
    echo "9 4 2" > /home/www/siom/grader/tasks/pomidorai_jau/00.in && \
    echo "4" > /home/www/siom/grader/tasks/pomidorai_jau/00.sol && \
    echo "5 3 1" > /home/www/siom/grader/tasks/pomidorai_jau/01.in && \
    echo "2" > /home/www/siom/grader/tasks/pomidorai_jau/01.sol


