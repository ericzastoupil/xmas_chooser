Script to assign gift relationships. Given a file with participants, assigns a gift receiver to a gift giver.

Built in spouse-checking to ensure spouses are not assigned to each other.

Ability to display pairings to the screen or send private emails.

Usage: xmas chooser [-h] (-p | -e EMAIL) -f FILE [-r]

Assigns secret (or not secret) gift pairings

optional arguments:
  -h, --help            show this help message and exit
  -p, --print           print assignments to console. not a secret
  -e EMAIL, --email EMAIL
                        email assignments. keeps things a secret. pass in config file if using this switch
  -f FILE, --file FILE  participant file (.jsonl): one JSON object per line with name, email, dont_gift
  -r, --real            set this to send the real assignment emails

Participant file format (JSON Lines, `.jsonl`): one participant per line. `dont_gift` lists names of other participants this person must not be assigned. See `participants.jsonl` for an example:

    {"name": "name1", "email": "email1", "dont_gift": ["name2"]}
    {"name": "name2", "email": "email2", "dont_gift": ["name1"]}

Files named `*_participants.jsonl` are git-ignored so real participant lists stay out of the repo.
