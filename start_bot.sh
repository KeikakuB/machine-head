#!/bin/bash
FILE='bot.pid'
ID=$(<"$FILE")
# Kill the bot if needed
kill "$ID"
# Start the bot and store its pid in 'bot.pid' file
machine_head & echo $! > "$FILE"
