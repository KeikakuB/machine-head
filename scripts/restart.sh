#!/bin/bash
cd ..
. venv/bin/activate
pkill machine_head
nohup machine_head > log/shell.out 2> log/shell.err < /dev/null &

