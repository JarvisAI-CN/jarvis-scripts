#!/bin/bash
for i in {1..30}; do
    lsof -u www-data | grep -E "temp|upload|download|ncm"
    sleep 1
done
