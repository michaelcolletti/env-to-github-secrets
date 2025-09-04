#!/bin/bash
for i in `gh repo list | awk '{print$1}'`
do
python src/main.py list-secrets -r $i
done
