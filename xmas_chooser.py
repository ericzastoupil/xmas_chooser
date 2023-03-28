import csv, random, smtplib, argparse, configparser


class Participant():
    def __init__(self, name, spouse, email, dont_gift):
        self.name = name
        self.spouse = spouse
        self.email = email
        self.dont_gift = dont_gift

def parse_command_line():
    parser = argparse.ArgumentParser(prog='xmas chooser', description='Assigns secret (or not secret) gift pairings')
    p_e_group = parser.add_mutually_exclusive_group(required=True)
    p_e_group.add_argument('-p', '--print', action='store_true', help='print assignments to console. not a secret')
    p_e_group.add_argument('-e','--email', type=str, help='email assignments. keeps things a secret. pass in config file (required) if using this switch')
    parser.add_argument('-f', '--file', type=str, required=True, help="file with participant info (required)")
    parser.add_argument('-r', '--real', action='store_true', help='set this to send the real assignment emails')

    return parser.parse_args()

def create_assignments(givers, receivers):

    invalid = True

    #Loop until no one is giving to himself/herself, their spouse, or a don't gifter
    while invalid:
        invalid = False
        random.shuffle(receivers)
    
        #If giving to yourself/your spouse/someone you're not allowed to, make this run invalid
        for giver, receiver in zip(givers, receivers):
            if giver.name == receiver.name:
                invalid = True
            elif giver.spouse == receiver.name:
                invalid = True
            elif receiver.name in giver.dont_gift:
                invalid = True

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

def create_list(file_name):
    givers = []
    
    with open(file_name) as file:
        reader = csv.reader(file)
        next(reader)

        #each line in the file (structured as a list)
        for l in reader:
            name, spouse, email, *dont_gift = l

            #create the participant and add to the givers list
            p = Participant(name, spouse, email, dont_gift)
            givers.append(p)
        
    return givers

if __name__ == '__main__':

    #Take arguments from the command line
    args = parse_command_line()

    #Create initial list based on file to read in
    givers = create_list(args.file)

    #Create a whole new list to represent the receivers of gifts
    receivers = givers.copy()

    #Mix up receivers to create assignments
    create_assignments(givers, receivers)

    #either print or email results
    if args.print:
        print_results(givers, receivers)
    elif args.email:
        email_results(args.email, givers, receivers, args.real)