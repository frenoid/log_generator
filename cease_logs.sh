#!/bin/bash

export pid=`ps -ef | grep 'python.*[ ]src/generate_webserver_logs.py' | awk 'NR==1{print $2}' | cut -d' ' -f1`;kill $pid
echo "Stop writing logs to logs/webserver.log"
exit 0

