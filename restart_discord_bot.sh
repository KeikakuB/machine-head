#!/bin/bash
cd ~/projects/machine-head/
git pull
. venv/bin/activate
nohup ./start_bot.sh &
