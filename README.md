# machine-head
Personal Discord bot
- Supports public polls, dice rolling, events


# TODO
- dev:
    - put extensions into .json file [ {name: x, is_startup: true } , ...]
    - Implement command for resetting the db, don't always do it reeeeeeeeeeeeeeeeee
    - put dev commands in dev module -> it'll work now because I'll import the things i need eg. subprocess
        - only enable it in dev bot
- Event Reminders:
    - Implement !remind *event_id* *message* *timedelta=defaults to at time of meeting*
        - does a @everyone with the event details and the reminder message in the given channel
- Logging:
    - figure out how to actually see errors as they are raised
    - setup logging everywhere with logger
- Polls:
    - Prevent people from reacting to polls with non-standard reactions
    - Add mutually exclusive polls which allow people to react in one way to a poll at a time
- Events:
    - Don't delete data on production server and solidify info I need per event
    - Implement join and leave commands
- Looking to play:
    - Design and test some sort of "looking to play" feature
