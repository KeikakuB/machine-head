# machine-head
Personal Discord bot
- Supports public polls, dice rolling, events


# TODO
- dev:
    - put extensions into .json file [ {name: x, is_startup: true } , ...]
    - Implement command for resetting the db, don't always do it reeeeeeeeeeeeeeeeee
    - put dev commands in dev module -> it'll work now because I'll import the things i need eg. subprocess
        - only enable it in dev bot
    - if no json data then create it with no values
    - https://github.com/JellyWX/reminder-bot/blob/master/Bot/main.py
    - add member tracking of most recent games they've played
    - try this again https://docs.python.org/2/library/sqlite3.html#sqlite3.Connection.row_factory
    - add option to insert test data by default when resetting the db
    - Make '!cmd' run its default command
    - Make bot usable in dm!? And on other servers
    - Add uptime command to bot

- Event Reminders:
    - Implement !remind *event_id* *message* *timedelta=defaults to at time of meeting*
        - does a @everyone with the event details and the reminder message in the given channel
- Logging:
    - figure out how to actually see errors as they are raised
    - setup logging everywhere with logger
- Polls:
    - Prevent people from reacting to polls with non-standard reactions
    - Add tracking for polls in the db and add a !poll results command and put polls into their own plugin
    - Add mutually exclusive polls which allow people to react in one way to a poll at a time
- Events:
    - Don't delete data on production server and solidify info I need per event
    - Implement join and leave commands
- Looking to play:
    - Design and test some sort of "looking to play" feature
