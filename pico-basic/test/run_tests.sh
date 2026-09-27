#!/bin/sh
# programs/*.in をインタプリタに流し、programs/*.out と一致するか調べる。
# 期待値を作り直すとき: ./run_tests.sh --update
cd "$(dirname "$0")"
fail=0
for in in programs/*.in; do
  out=${in%.in}.out
  work=$(mktemp -d)
  (cd "$work" && "$OLDPWD/basic" < "$OLDPWD/$in") > "$work/actual" 2>&1
  if [ "$1" = "--update" ]; then
    cp "$work/actual" "$out"
    echo "updated $out"
  elif diff -u "$out" "$work/actual" > "$work/diff"; then
    echo "ok   $in"
  else
    echo "FAIL $in"; cat "$work/diff"; fail=1
  fi
  rm -rf "$work"
done
exit $fail
