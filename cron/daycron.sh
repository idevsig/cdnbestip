#!/usr/bin/env bash

set -e

# shellcheck disable=SC1091
. ./include/cdnbestip.sh

LOG_PATH="./cronday.log"
{
  echo
  date
} >>$LOG_PATH

cdnbestip >>$LOG_PATH

echo

##
# crontab
# 36 3 * * * root cd /root/shfiles; bash ./daycron.sh
##
