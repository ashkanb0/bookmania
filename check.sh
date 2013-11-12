#!/bin/bash
# My first script
echo "--------------------------------------------------------------"
echo "Checking for auctions on a day" 
echo "Date is:"
date '+%Y-%m-%d'
python /home/ashkan/Desktop/bookmania/manage.py checkauctions
echo "--------------------------------------------------------------"
