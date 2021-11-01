#!/bin/bash

cd /opt/gen_logs
src/generate_webserver_logs.py > logs/webserver.log & echo "writing logs to logs/webserver.log" & exit 0
