# machine-head
Personal Discord bot
- Supports public polls, dice rolling, events


# TODO
- dev:
    - use shorter names (search == find, event == plan?, etc.)
    - assign to no_pm=true to commands appropriately eg. events, polls
    - test that is_owner code actually works
    - double check 'checks' code
    - put common code somewhere (eg. json reading code, etc.)
    - if no json data exists then create a template for it, log it and exit
    - https://github.com/JellyWX/reminder-bot/blob/master/Bot/main.py
    - add member tracking of most recent games they've played?
    - try this again https://docs.python.org/2/library/sqlite3.html#sqlite3.Connection.row_factory
    - Make '!cmd' run its default command
    - Design data such that same bot instance will work in multiple servers (data/db? anything else?)
- Event Reminders:
    - Implement !remind *event_id* *message* *timedelta=defaults to at time of meeting*
        - message can contain @mentions, but defaults to only mentioning person who set the reminder
- Logging:
    - figure out how to actually see errors as they are raised
    - setup logging everywhere with logger
- Polls:
    - Prevent people from reacting to polls with non-standard reactions
    - Add tracking for polls in the db and add a !poll results command and put polls into their own plugin
    - Add mutually exclusive polls which allow people to react in one way to a poll at a time
- Events:
    - Don't throw error when specifying an non-existing event to edit

- Looking to play:
    - Design and test some sort of "looking to play" feature
