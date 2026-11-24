import argparse
import configparser
import json
import os
import random
import re
import smtplib
import sys

from participant import Participant

def parse_command_line():
    parser = argparse.ArgumentParser(prog='xmas chooser', description='Assigns secret (or not secret) gift pairings')
    p_e_group = parser.add_mutually_exclusive_group(required=True)
    p_e_group.add_argument('-p', '--print', action='store_true', help='print assignments to console. not a secret')
    p_e_group.add_argument('-e','--email', type=str, help='email assignments. keeps things a secret. pass in config file (required) if using this switch')
    parser.add_argument('-f', '--file', type=str, required=True, help="participant file (.jsonl): one JSON object per line with name, email, dont_gift (required)")
    parser.add_argument('-l', '--last-year', type=str, help="last year's pairings, in the 'X gets a gift for Y' format that -p prints. those pairings won't be repeated")
    parser.add_argument('-o', '--output', type=str, help="save pairings to this file (won't overwrite an existing file). pass it to -l next year")
    parser.add_argument('-r', '--real', action='store_true', help='set this to send the real assignment emails')

    return parser.parse_args()

MAX_ATTEMPTS = 10000

def is_valid_pair(giver, receiver):
    return giver.name != receiver.name and receiver.name not in giver.dont_gift

def create_assignments(givers):
    receivers = givers.copy()

    #Shuffle until no one is giving to themselves or someone on their dont_gift list
    for _ in range(MAX_ATTEMPTS):
        random.shuffle(receivers)
        if all(is_valid_pair(g, r) for g, r in zip(givers, receivers)):
            return receivers

    raise RuntimeError(
        f"Could not find a valid assignment after {MAX_ATTEMPTS} attempts. "
        "Check that the dont_gift lists (and last year's pairings, if given) leave everyone "
        "at least one possible receiver."
    )

def email_results(config_file, givers, receivers, real):
    print("[+] Emailing results...")

    config = configparser.ConfigParser()
    config.read(config_file)
    
    port = int(config['DEFAULT']['SSL_PORT'])
    server = config['DEFAULT']['SMTP_SERVER']
    sender_mail = config['DEFAULT']['SENDER_EMAIL']
    password = config['DEFAULT']['SENDER_EMAIL_PASSWORD']

    for giver, receiver in zip(givers, receivers):
        
        message = f"""\
            Subject: Your secret santa selection

            Hi {giver.name},
            You will give a gift to {receiver.name}
            """
        
        s = smtplib.SMTP_SSL(server, port)
        s.login(sender_mail, password)

        if real:
            #don't uncomment until game time
            #s.sendmail(sender_mail, giver.email, message)
            pass
        else:
            s.sendmail(sender_mail, sender_mail, message)
                    
        s.quit()
        
        print(f'[+] Email sent to {giver.name} at address {giver.email}')

def format_pairing(giver, receiver):
    #Must stay in sync with PAIRING_PATTERN so saved output can be read back with -l
    return f'{giver.name} gets a gift for {receiver.name}'

def print_results(givers, receivers):
    for giver, receiver in zip(givers, receivers):
        print(format_pairing(giver, receiver))

def save_results(file_name, givers, receivers):
    #'x' mode refuses to overwrite an existing file
    with open(file_name, 'x') as file:
        for giver, receiver in zip(givers, receivers):
            file.write(format_pairing(giver, receiver) + '\n')
    print(f'[+] Pairings saved to {file_name}', file=sys.stderr)

REQUIRED_KEYS = ("name", "email", "dont_gift")

def create_list(file_name):
    givers = []
    errors = []

    with open(file_name) as file:
        for line_num, line in enumerate(file, start=1):
            #Skip blank lines
            if not line.strip():
                continue

            try:
                pDict = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {line_num}: invalid JSON ({e.msg})")
                continue

            missing = [key for key in REQUIRED_KEYS if key not in pDict]
            if missing:
                errors.append(f"line {line_num}: missing {', '.join(missing)}")
                continue

            if not isinstance(pDict["dont_gift"], list):
                errors.append(f"line {line_num}: dont_gift must be a list of names")
                continue

            givers.append(Participant(pDict["name"], pDict["email"], pDict["dont_gift"]))

    #Names are used to match people, so they must be unique
    names = [p.name for p in givers]
    for name in sorted({n for n in names if names.count(n) > 1}):
        errors.append(f"duplicate name: {name}")

    #Every dont_gift entry must be a real participant (catches typos)
    for p in givers:
        for blocked in p.dont_gift:
            if blocked not in names:
                errors.append(f"{p.name}'s dont_gift has unknown name: {blocked!r}")

    if errors:
        raise ValueError(f"Problems in {file_name}:\n  " + "\n  ".join(errors))

    return givers

PAIRING_PATTERN = re.compile(r"^(.+) gets a gift for (.+)$")

def apply_last_year(file_name, givers):
    """Read last year's 'X gets a gift for Y' lines and add each Y to X's dont_gift."""
    by_name = {p.name: p for p in givers}
    seen_givers = set()
    errors = []

    with open(file_name) as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue

            match = PAIRING_PATTERN.match(line)
            if not match:
                errors.append(f"line {line_num}: expected 'X gets a gift for Y', got {line!r}")
                continue

            giver_name, receiver_name = match.groups()
            if giver_name in seen_givers:
                errors.append(f"line {line_num}: {giver_name} is listed as a giver more than once")
                continue
            seen_givers.add(giver_name)

            #Someone not participating this year is fine, but warn in case it's a typo
            unknown = [n for n in (giver_name, receiver_name) if n not in by_name]
            if unknown:
                print(f"[!] {file_name} line {line_num}: ignored, not in this year's list: {', '.join(unknown)}",
                      file=sys.stderr)
                continue

            giver = by_name[giver_name]
            if receiver_name not in giver.dont_gift:
                giver.dont_gift.append(receiver_name)

    if errors:
        raise ValueError(f"Problems in {file_name}:\n  " + "\n  ".join(errors))

def main():
    #Take arguments from the command line
    args = parse_command_line()

    #Fail before doing any work if the output file would be overwritten
    if args.output and os.path.exists(args.output):
        raise SystemExit(f"[-] {args.output} already exists. Choose a different -o file or remove it first.")

    #Create initial list based on file to read in
    try:
        givers = create_list(args.file)

        #Don't repeat last year's giver -> receiver pairings
        if args.last_year:
            apply_last_year(args.last_year, givers)
    except ValueError as e:
        raise SystemExit(f"[-] {e}")

    #Mix up a copy of the givers to create assignments
    try:
        receivers = create_assignments(givers)
    except RuntimeError as e:
        raise SystemExit(f"[-] {e}")

    #Save before printing/emailing so the pairings are kept even if emailing fails partway
    if args.output:
        save_results(args.output, givers, receivers)

    #either print or email results
    if args.print:
        print_results(givers, receivers)
    elif args.email:
        email_results(args.email, givers, receivers, args.real)

if __name__ == '__main__':
    main()