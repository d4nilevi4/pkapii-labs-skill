#!/bin/sh
# browsershot.sh OUT.png URL [WIDTH HEIGHT] -- screenshot of a page in headless Chrome (throwaway profile)
P=$(mktemp -d)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --user-data-dir="$P" --window-size=${3:-1100},${4:-640} --virtual-time-budget=8000 --screenshot="$1" "$2" >/dev/null 2>&1
rm -rf "$P"; ls -l "$1" | awk '{print $5, $9}'
