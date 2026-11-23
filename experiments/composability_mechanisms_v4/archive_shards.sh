#!/bin/bash
# Archive post-lock chain shards (results/shards, not in git) into results/shards_<unit>_<bb>[_<domain>].tar.xz, each < 50 MB.
set -euo pipefail
cd "$(dirname "$0")/results"
ls shards > /tmp/shardlist.$$
mk(){ local out=$1; shift; grep -E "$@" /tmp/shardlist.$$ | sed 's|^|shards/|' > /tmp/sel.$$; tar -cJf "$out" -T /tmp/sel.$$; echo "$out $(wc -l < /tmp/sel.$$) files $(du -m "$out" | cut -f1) MB"; }
mk shards_B_bart.tar.xz '^chain_bart_(bind3|name3|bind3fix)_'
for bb in bart t5; do
  mk shards_D_$bb.tar.xz "^chain_${bb}_[a-z0-9]+_natural_D_"
  for d in weekday month compass hour compass8 season; do
    grep -qE "^chain_${bb}_${d}_natural_" /tmp/shardlist.$$ || continue
    mk shards_L_${bb}_${d}.tar.xz "^chain_${bb}_${d}_natural_([^D]|D[^_])"
  done
done
rm -f /tmp/shardlist.$$ /tmp/sel.$$
