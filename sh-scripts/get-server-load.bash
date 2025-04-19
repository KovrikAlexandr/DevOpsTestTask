#!/bin/bash

awk -v cores="$(nproc)" '{print $3 / cores}' /proc/loadavg
free -m | awk '/Mem:/ {print $7}'
df -m / | awk 'NR == 2 {print $4}'
