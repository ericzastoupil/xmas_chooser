import random, smtplib, argparse, configparser, json
from participant import Participant

def parse_command_line():
    parser = argparse.ArgumentParser(prog='xmas chooser', description='Assigns secret (or not secret) gift pairings')
    p_e_group = parser.add_mutually_exclusive_group(required=True)
    p_e_group.add_argument('-p', '--print', action='store_true', help='print assignments to console. not a secret')
    p_e_group.add_argument('-e','--email', type=str, help='email assignments. keeps things a secret. pass in config file (required) if using this switch')
    parser.add_argument('-f', '--file', type=str, required=True, help="file with participant info (required)")
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
        "Check that the dont_gift lists leave everyone at least one possible receiver."
    )

def email_results(config_file, givers, receivers, real):
    print(f"[+] Emailing results...")

    config = configparser.ConfigParser()
    config.read(config_file)
    
    port = int(config['DEFAULT']['SSL_PORT'])
    server = str(config['DEFAULT']['SMTP_SERVER'])
    sender_mail = str(config['DEFAULT']['SENDER_EMAIL'])
    password = str(config['DEFAULT']['SENDER_EMAIL_PASSWORD'])

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
        
        print(f'[+] Email sent to {giver.name} at address {giver.email}:')

def print_results(givers, receivers):
    for giver, receiver in zip(givers, receivers):
        print(f'{giver.name} gets a gift for {receiver.name}')

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

if __name__ == '__main__':

    #Take arguments from the command line
    args = parse_command_line()

    #Create initial list based on file to read in
    try:
        givers = create_list(args.file)
    except ValueError as e:
        raise SystemExit(f"[-] {e}")

    #Mix up a copy of the givers to create assignments
    receivers = create_assignments(givers)

    #either print or email results
    if args.print:
        print_results(givers, receivers)
    elif args.email:
        email_results(args.email, givers, receivers, args.real)