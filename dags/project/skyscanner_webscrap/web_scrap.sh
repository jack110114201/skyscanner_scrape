#!/bin/bash

# 切換當前工作目錄到腳本所在的目錄
cd "${0%/*}"

takeoff=$1
landoff=$2
takeoff_date=$3

python3 web_scrap.py $1 $2 $3

