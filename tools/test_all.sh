#!/bin/sh
# Rebuild, then run every browser test suite. Usage: sh tools/test_all.sh [screenshot_dir]
cd "$(dirname "$0")/.." && node tools/build.js > /dev/null || exit 1
cd tools
OUT=${1:-.}
fail=0
for t in test test_picture test_games test_games2 test_games3 test_games4 test_games5 test_learn test_checkpoint test_howto; do
  res=$(timeout 900 python3 $t.py "$OUT" 2>&1)
  passed=$(printf "%s\n" "$res" | grep -c "^PASS")
  last=$(printf "%s\n" "$res" | tail -1)
  printf "%-16s %3s checks  %s\n" "$t" "$passed" "$last"
  printf "%s\n" "$res" | grep "^FAIL"
  [ "$last" = "ALL PASSED" ] || fail=1
done
exit $fail
