#!/bin/bash
# Usage: ledger.sh UNIT LANE JOBID [UNIT LANE JOBID ...]  -- appends/updates sacct records in run_ledger.json
set -euo pipefail
cd "$(dirname "$0")"
[ -f run_ledger.json ] || echo '{"budget_gpu_hours":16,"jobs":[]}' > run_ledger.json
while [ $# -ge 3 ]; do
  unit=$1 lane=$2 id=$3; shift 3
  line=$(sacct -j "$id" -X -n -P -o JobID,JobName,State,ElapsedRaw,AllocTRES,Partition,NodeList,Start,End | head -1)
  IFS='|' read -r jid name state elapsed tres part node start end <<< "$line"
  gpus=$(echo "$tres" | grep -o 'gres/gpu=[0-9]*' | cut -d= -f2 || true); gpus=${gpus:-0}
  jq --arg unit "$unit" --arg lane "$lane" --arg id "$jid" --arg name "$name" --arg state "$state" \
     --argjson elapsed "${elapsed:-0}" --argjson gpus "$gpus" --arg tres "$tres" --arg part "$part" --arg node "$node" \
     --arg start "$start" --arg end "$end" '
    .jobs = ([.jobs[] | select(.job_id != $id)] + [{unit:$unit,lane:$lane,job_id:$id,name:$name,state:$state,elapsed_s:$elapsed,
      gpus:$gpus,gpu_hours:($elapsed*$gpus/3600),alloc_tres:$tres,partition:$part,node:$node,start:$start,end:$end}])
    | .total_gpu_hours = ([.jobs[].gpu_hours] | add)' run_ledger.json > run_ledger.json.tmp && mv run_ledger.json.tmp run_ledger.json
done
jq -r '"total GPU h: \(.total_gpu_hours)"' run_ledger.json
