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
  -f FILE, --file FILE  file with participant info
  -r, --real            set this to send the real assignment emails
