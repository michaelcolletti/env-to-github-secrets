#!/bin/bash
for i in `gh repo list | awk '{print$1}'`
do
python src/env-to-github-secrets.py list-secrets -r $i
done
