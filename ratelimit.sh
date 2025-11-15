#!/bin/sh

docker exec dummydockernetworking-talker-1 tc qdisc replace dev eth0 root tbf rate $1 burst 32kbit latency 400ms