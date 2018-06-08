#!/bin/bash
cd ~/projects/machine-head/
. venv/bin/activate
nohup ./start_bot.sh > log/shell.out 2> log/shell.err < /dev/null &

