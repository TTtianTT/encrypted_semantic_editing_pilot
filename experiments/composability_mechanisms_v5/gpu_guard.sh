#!/bin/bash
# GPUs in use now, or able to start at once (pending without dependency).
need=${1:-1}
used=$(squeue -u "$USER" -h -t R,PD -o "%T|%E|%b" | awk -F'|' '
  { n=0; if (match($3, /gpu[:=]([A-Za-z0-9_]+[:=])?[0-9]+/)) { s=substr($3, RSTART, RLENGTH); k=split(s, a, /[:=]/); n=a[k] } }
  $1=="RUNNING" || ($1=="PENDING" && ($2=="" || $2=="(null)")) { u+=n }
  END { print u+0 }')
if [ $((used + need)) -gt 2 ]; then echo "GPU busy: ${used} in use"; exit 1; fi
echo "GPU ok: ${used} in use"
