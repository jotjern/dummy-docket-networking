#!/bin/sh
set -eu

# cap talker egress so the monitor sees < 1 MB/s
tc qdisc replace dev eth0 root tbf rate 800kbit burst 32kbit latency 400ms

exec "$@"
