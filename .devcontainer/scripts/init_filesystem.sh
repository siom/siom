#!/bin/bash
set -e

mkdir -p "$SIOM_HOME/logs"
mkdir -p "$SIOM_HOME/grader/tasks"
ln -s /workspace "$SIOM_HOME/web"
