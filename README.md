Script to assign gift relationships. Given a file with participants, assigns each gift giver a gift receiver.

No one is assigned to themselves, and each participant can list people they must not be assigned (for example, a spouse or siblings) in `dont_gift`.

Pairings can be printed to the screen or sent as private emails.

```
usage: xmas chooser [-h] (-p | -e EMAIL) -f FILE [-r]

Assigns secret (or not secret) gift pairings

options:
  -h, --help         show this help message and exit
  -p, --print        print assignments to console. not a secret
  -e, --email EMAIL  email assignments. keeps things a secret. pass in config file (required) if
                     using this switch
  -f, --file FILE    participant file (.jsonl): one JSON object per line with name, email,
                     dont_gift (required)
  -r, --real         set this to send the real assignment emails
```

Examples:

    python3 xmas_chooser.py -p -f participants.jsonl
    python3 xmas_chooser.py -e config.ini -f adults_participants.jsonl

Participant file format (JSON Lines, `.jsonl`): one participant per line. `dont_gift` lists names of other participants this person must not be assigned. See `participants.jsonl` for an example:

    {"name": "name1", "email": "email1", "dont_gift": ["name2"]}
    {"name": "name2", "email": "email2", "dont_gift": ["name1"]}

The file is checked before any pairings are made: bad JSON, missing fields, duplicate names, and `dont_gift` names that don't match a participant are all reported. If the `dont_gift` rules make a pairing impossible, the script says so instead of running forever.

Files named `*_participants.jsonl` are git-ignored so real participant lists stay out of the repo.

Email settings (SMTP server, port, sender account and password) are read from the config file passed to `-e`; see `config.ini` for the expected keys.
