#!/bin/bash
set -e

sudo apt-get install -y libcap-dev
mkdir -p "$SANDBOX_HOME"
git clone https://github.com/ioi/isolate.git "$SANDBOX_HOME"
cd "$SANDBOX_HOME"
git checkout v1.4.1
make isolate
sudo cp isolate isolate-check-environment /usr/local/bin
sudo chmod 4755 /usr/local/bin/isolate
sudo ln -s /workspace/.devcontainer/isolate_config.txt /usr/local/etc/isolate

ln -s "$SIOM_HOME/grader/tasks" "$SIOM_HOME/sandbox/tasks"
ln -s "$SIOM_HOME/web/grader/checker.py" "$SIOM_HOME/sandbox/checker.py"