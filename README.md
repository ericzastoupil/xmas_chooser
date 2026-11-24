Script to assign gift relationships. Given a file with participants, assigns each gift giver a gift receiver.

No one is assigned to themselves, and each participant can list people they must not be assigned (for example, a spouse or siblings) in `dont_gift`.

Pairings can be printed to the screen or sent as private emails.

```
usage: xmas chooser [-h] (-p | -e EMAIL) -f FILE [-l LAST_YEAR] [-o OUTPUT] [-r]

Assigns secret (or not secret) gift pairings

options:
  -h, --help            show this help message and exit
  -p, --print           print assignments to console. not a secret
  -e, --email EMAIL     email assignments. keeps things a secret. pass in config file (required)
                        if using this switch
  -f, --file FILE       participant file (.jsonl): one JSON object per line with name, email,
                        dont_gift (required)
  -l, --last-year LAST_YEAR
                        last year's pairings, in the 'X gets a gift for Y' format that -p prints.
                        those pairings won't be repeated
  -o, --output OUTPUT   save pairings to this file (won't overwrite an existing file). pass it to
                        -l next year
  -r, --real            set this to send the real assignment emails
```

Examples:

    python3 xmas_chooser.py -p -f participants.jsonl
    python3 xmas_chooser.py -e config.ini -f adults_participants.jsonl

Avoiding last year's pairings: save each year's pairings with `-o`, then pass that file back with `-l` the next year. No giver will be assigned the same receiver as last year. `-o` won't overwrite an existing file, and it saves the pairings before printing or emailing them.

    python3 xmas_chooser.py -p -f adults_participants.jsonl -o adults_pairings_2026.txt
    python3 xmas_chooser.py -p -f adults_participants.jsonl -l adults_pairings_2026.txt -o adults_pairings_2027.txt   # next year

The `-l` file has one `X gets a gift for Y` line per pairing (blank lines are ignored). Malformed lines and a giver listed twice are errors. Names not in this year's participant file are skipped with a warning, so people who've dropped out don't cause problems.

Saved pairing files contain real names, so files named `*_pairings_*.txt` are git-ignored too.

Participant file format (JSON Lines, `.jsonl`): one participant per line. `dont_gift` lists names of other participants this person must not be assigned. See `participants.jsonl` for an example:

    {"name": "name1", "email": "email1", "dont_gift": ["name2"]}
    {"name": "name2", "email": "email2", "dont_gift": ["name1"]}

The file is checked before any pairings are made: bad JSON, missing fields, duplicate names, and `dont_gift` names that don't match a participant are all reported. If the `dont_gift` rules make a pairing impossible, the script says so instead of running forever.

Files named `*_participants.jsonl` are git-ignored so real participant lists stay out of the repo.

Email settings (SMTP server, port, sender account and password) are read from the config file passed to `-e`; see `config.ini` for the expected keys.
