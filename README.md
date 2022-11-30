Script to assign gift relationships. Given a file with participants, assigns a gift receiver to a gift giver.

Built in spouse-checking to ensure spouses are not assigned to each other.

Ability to display pairings to the screen or send private emails.

USAGE:
optional arguments:
  -h, --help            show this help message and exit
  -e, --email           email assignments. keeps things a secret
  -p, --print           print assignments to console. not a secret
  -f FILE, --file FILE  file with participant info
  -c CONFIG, --config CONFIG
                        config file for emails. default is config.ini
  -r, --real            set this to send the real assignment emails
