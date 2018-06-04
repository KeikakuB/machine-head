# machine-head
Personal Discord bot
- Supports public polls, dice rolling, events


# TODO
- dev:
    - put common code somewhere (eg. json reading code, is_admin, etc.)
    - Implement command for resetting the db, don't always do it reeeeeeeeeeeeeeeeee
        - Don't delete data on production server and solidify info I need per event
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
    - Implement join and leave commands
- Looking to play:
    - Design and test some sort of "looking to play" feature
