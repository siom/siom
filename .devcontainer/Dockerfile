# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.194.0/containers/ubuntu/.devcontainer/base.Dockerfile

FROM mcr.microsoft.com/vscode/devcontainers/base:0.202.0-ubuntu-18.04

RUN apt-get update && \
    apt-get install -y make build-essential libssl1.0-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev

# Give the vscode user access to the /home/www directory
RUN mkdir /home/www && chown -R vscode:vscode /home/www

WORKDIR /home/vscode
USER vscode

ENV HOME="/home/vscode"
ENV PYENV_ROOT="$HOME/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
ENV SIOM_HOME="/home/www/siom"
ENV SANDBOX_HOME="$SIOM_HOME/sandbox"

COPY .devcontainer/scripts/init_python.sh ./.devcontainer/scripts/init_python.sh
RUN .devcontainer/scripts/init_python.sh

# Install some additional necessary dependencies
# * default-libmysqlclient-dev is needed for MySQL-python, but for some reason it won't install together with all other libs defined above
# * mysql-client-core-5.7 allows us to inspect the underlying database
# * texlive and dvipng are needed when rendering latex on the website
RUN sudo apt-get install -y default-libmysqlclient-dev mysql-client-core-5.7 texlive dvipng

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .devcontainer/scripts/init_filesystem.sh ./.devcontainer/scripts/init_filesystem.sh
RUN .devcontainer/scripts/init_filesystem.sh
COPY .devcontainer/scripts/init_sandbox.sh ./.devcontainer/scripts/init_sandbox.sh
RUN .devcontainer/scripts/init_sandbox.sh

# Copy the rest of the contents of .devcontainer
COPY .devcontainer/ ./.devcontainer/
COPY manage.py .

# Seed filesystem
RUN .devcontainer/scripts/seed_filesystem.sh
