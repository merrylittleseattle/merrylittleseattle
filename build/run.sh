#!/bin/sh
# Usage: sh build/run.sh <events_dump.json> <bars_dump.json> [tabs_dump.json]
# Each dump is the JSON saved from Google Sheets get_values:
#   events: 'Events'!A1:T600   bars: 'Christmas Pop Up Bars'!A1:N80
set -e
cd "$(dirname "$0")"
# optional third argument: Give Back / Holiday Drives / Meal Kitchens dump
if [ -n "$3" ]; then python3 tabs.py "$3"; fi
python3 make_raw.py "$1"
python3 bars.py "$2" "$1"
python3 build_data.py
python3 build.py
cp index.html ../index.html
