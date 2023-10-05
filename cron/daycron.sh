#!/usr/bin/env bash

set -e

. ./include/cdnbestip.sh

LOG_PATH="./cronday.log"
echo >>$LOG_PATH
date >>$LOG_PATH

cdnbestip >>$LOG_PATH

echo

##
# crontab
# 36 3 * * * root cd /root/shfiles; bash ./daycron.sh
##
