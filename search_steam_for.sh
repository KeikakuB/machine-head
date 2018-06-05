PATTERN_SEARCH_TERM="{[^{]*$1[^}]*}"
PATTERN_APP_ID='"appid":[[:digit:]]*'
PATTERN_ID='[[:digit:]]*'
grep -o "$PATTERN_SEARCH_TERM" secret/steamapps.json | \
grep -o "$PATTERN_APP_ID" | \
grep -o -m 1 "$PATTERN_ID"
