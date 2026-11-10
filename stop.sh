#!/bin/bash
cd "$(dirname "$0")"
pm2 stop ecosystem.config.json
pm2 save
pm2 ls
