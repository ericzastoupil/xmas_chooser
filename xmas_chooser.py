import argparse
import configparser
import json
import os
import random
import re
import smtplib
import sys
from email.message import EmailMessage

from participant import Participant

def parse_command_line(argv=None):
    parser = argparse.ArgumentParser(prog='xmas chooser', description='Assigns secret (or not secret) gift pairings')
    p_e_group = parser.add_mutually_exclusive_group(required=True)
    p_e_group.add_argument('-p', '--print', action='store_true', help='print assignments to console. not a secret')
    p_e_group.add_argument('-e', '--email', action='store_true', help='email assignments. keeps things a secret. email settings come from the -c file')
    parser.add_argument('-f', '--file', type=str, required=True, help="participant file (.jsonl): one JSON object per line with name, email, dont_gift (required)")
    parser.add_argument('-l', '--last-year', type=str, help="last year's pairings, in the 'X gets a gift for Y' format that -p prints. those pairings won't be repeated")
    parser.add_argument('-o', '--output', type=str, help="save pairings to this file (won't overwrite an existing file). pass it to -l next year")
    parser.add_argument('-c', '--config', type=str, default='config.ini', help='email settings file (default: config.ini). copy config.example.ini to make one')
    parser.add_argument('-r', '--real', action='store_true', help="with -e: email each person their own assignment. without -r, every email goes to the sender's own address as a test")

    args = parser.parse_args(argv)

    #If emailing fails partway, a rerun would reshuffle, so the pairings must be saved first
    if args.email and args.real and not args.output:
        parser.error("-e -r also needs -o FILE, so the pairings are saved in case emailing fails partway")

    return args

MAX_ATTEMPTS = 100000

def is_valid_pair(giver, receiver):
    return giver.name != receiver.name and receiver.name not in giver.dont_gift

def create_assignments(givers):
    """Seat everyone around one big circle; each person gives to the next person in it.

    A single circle means no two people simply swap gifts with each other
    (A gives to B and B gives to A), unless there are only two people.
    """
    circle = givers.copy()

    for _ in range(MAX_ATTEMPTS):
        random.shuffle(circle)
        next_in_circle = {circle[i].name: circle[(i + 1) % len(circle)] for i in range(len(circle))}
        receivers = [next_in_circle[g.name] for g in givers]
        if all(is_valid_pair(g, r) for g, r in zip(givers, receivers)):
            return receivers

    raise RuntimeError(
        f"Could not find a valid gift circle after {MAX_ATTEMPTS} attempts. "
        "Check that the dont_gift lists (and last year's pairings, if given) leave everyone "
        "enough possible receivers."
    )

EMAIL_KEYS = ("SSL_PORT", "SMTP_SERVER", "SENDER_EMAIL", "SENDER_EMAIL_PASSWORD")

def load_email_config(config_file):
    if not os.path.exists(config_file):
        raise ValueError(f"Email settings file {config_file} not found. Copy config.example.ini to {config_file} and fill it in.")

    config = configparser.ConfigParser()
    config.read(config_file)
    section = config['DEFAULT']

    missing = [key for key in EMAIL_KEYS if key not in section]
    if missing:
        raise ValueError(f"{config_file} is missing: {', '.join(missing)}")

    try:
        port = int(section['SSL_PORT'])
    except ValueError:
        raise ValueError(f"{config_file}: SSL_PORT must be a number, got {section['SSL_PORT']!r}")

    return {
        "port": port,
        "server": section['SMTP_SERVER'],
        "sender": section['SENDER_EMAIL'],
        "password": section['SENDER_EMAIL_PASSWORD'],
    }

def build_message(sender, to_address, giver, receiver, real):
    msg = EmailMessage()
    subject = "Your secret santa selection"
    msg['Subject'] = subject if real else f"[TEST for {giver.name}] {subject}"
    msg['From'] = sender
    msg['To'] = to_address
    msg.set_content(
        f"Hi {giver.name},\n\n"
        f"You will give a gift to {receiver.name}.\n\n"
        "Merry Christmas!\n"
    )
    return msg

def email_results(settings, givers, receivers, real):
    sender = settings["sender"]
    if real:
        print("[+] Emailing each person their assignment...")
    else:
        print(f"[+] TEST MODE: all emails go to {sender}. Add -r to send the real ones.")

    sent = []
    try:
        #One connection for the whole run instead of logging in once per person
        with smtplib.SMTP_SSL(settings["server"], settings["port"]) as s:
            s.login(sender, settings["password"])
            for giver, receiver in zip(givers, receivers):
                to_address = giver.email if real else sender
                s.send_message(build_message(sender, to_address, giver, receiver, real))
                sent.append(giver.name)
                print(f'[+] Email for {giver.name} sent to {to_address}')
    except (smtplib.SMTPException, OSError) as e:
        not_sent = [g.name for g in givers if g.name not in sent]
        raise RuntimeError(
            f"Emailing failed: {e}\n"
            f"  Sent: {', '.join(sent) or 'nobody'}\n"
            f"  Not sent: {', '.join(not_sent)}\n"
            "  Don't just rerun: that would reshuffle and give people conflicting assignments. "
            "The full pairings are in the -o file."
        )

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

def run(args):
    #Fail before doing any work if the output file would be overwritten
    if args.output and os.path.exists(args.output):
        raise ValueError(f"{args.output} already exists. Choose a different -o file or remove it first.")

    #Check email settings up front so a bad config doesn't waste a shuffle
    settings = load_email_config(args.config) if args.email else None

    #Create initial list based on file to read in
    givers = create_list(args.file)

    #Don't repeat last year's giver -> receiver pairings
    if args.last_year:
        apply_last_year(args.last_year, givers)

    receivers = create_assignments(givers)

    #Save before printing/emailing so the pairings are kept even if emailing fails partway
    if args.output:
        save_results(args.output, givers, receivers)

    #either print or email results
    if args.print:
        print_results(givers, receivers)
    elif args.email:
        email_results(settings, givers, receivers, args.real)

def main(argv=None):
    args = parse_command_line(argv)
    try:
        run(args)
    except OSError as e:
        #e.g. a mistyped -f or -l file name
        raise SystemExit(f"[-] Can't open {e.filename}: {e.strerror}" if e.filename else f"[-] {e}")
    except (ValueError, RuntimeError) as e:
        raise SystemExit(f"[-] {e}")

if __name__ == '__main__':
    main()
