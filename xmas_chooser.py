import csv, random, smtplib, ssl, argparse, configparser


class Participant():
    def __init__(self, name, spouse, email):
        self.name = name
        self.spouse = spouse
        self.email = email

def parse_command_line():
    parser = argparse.ArgumentParser(prog='xmas chooser', description='Assigns secret (or not secret) gift pairings')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e','--email', action='store_true', help='email assignments. keeps things a secret')
    group.add_argument('-p', '--print', action='store_true', help='print assignments to console. not a secret')
    parser.add_argument('-f', '--file', type=str, required=True, help="file with participant info")
    parser.add_argument('-c', '--config', type=str, default='config.ini', help='config file for emails. default is config.ini')
    parser.add_argument('-r', '--real', action='store_true', help='set this to send the real assignment emails')

    return parser.parse_args()

def create_assignments(givers, receivers):

    invalid = True

    #Loop until no one is giving to himself/herself or to their spouse
    while invalid:
        invalid = False
        random.shuffle(receivers)
    
        #If giving to yourself or your spouse, make this run invalid
        for i in range(len(givers)):
            if givers[i].name == receivers[i].name:
                invalid = True
            elif givers[i].spouse == receivers[i].name:
                invalid = True

def email_results(config_file, givers, receivers, real):
    print(f"[+] Emailing results...")

    config = configparser.ConfigParser()
    config.read(config_file)
    
    port = int(config['DEFAULT']['SSL_PORT'])
    server = str(config['DEFAULT']['SMTP_SERVER'])
    sender_mail = str(config['DEFAULT']['SENDER_EMAIL'])
    password = str(config['DEFAULT']['SENDER_EMAIL_PASSWORD'])

    for i in range(len(givers)):
        
        message = f"""\
            Subject: Your secret santa selection

            Hi {givers[i].name},
            You will give a gift to {receivers[i].name}
            """
        
        s = smtplib.SMTP_SSL(server, port)
        s.login(sender_mail, password)

        if real:
            #don't uncomment until game time
            #s.sendmail(sender_mail, givers[i].email, message)
            pass
        else:
            s.sendmail(sender_mail, sender_mail, message)
                    
        s.quit()
        
        print(f'[+] Email sent to {givers[i].name} at address {givers[i].email}:')

def print_results(givers, receivers):
    for i in range(len(givers)):
        print(f'{givers[i].name} gets a gift for {receivers[i].name}')

def create_list(file_name):
    givers = []

    with open(file_name) as file:
        reader = csv.reader(file)
        next(reader)
        
        for name, spouse, email in reader:
            p = Participant(name, spouse, email)
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
        email_results(args.config, givers, receivers, args.real)