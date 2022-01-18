import os
import sys
import ssl
import json
import email
import random
import getpass
import smtplib
import argparse
import email.utils
import email.policy
from email.message import EmailMessage


class SecretSanta:
    name: str
    email: str

    def __init__(self, name, email) -> None:
        self.name = name
        self.email = email

    def __str__(self) -> str:
        return f"Name: {self.name}, Email: {self.email}"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, self.__class__):
            return __o.name == self.name and __o.email == self.email
        return False

    def __hash__(self):
        return hash((self.name, self.email))


class Sender:
    address: str    # address of the sender server
    email: str      # email address, from which messages are being send
    port: int       # port, on which the server should listen
    subject: str    # subject of the email
    body: str       # body of the email

    def __init__(self, address: str, email: str, port: int, subject: str, body: str) -> None:
        self.address = address
        self.email = email
        self.port = port
        self.subject = subject
        self.body = body

    def __str__(self) -> str:
        return f"Email: {self.email}, Server Address: {self.email}, Port: {self.port}"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, self.__class__):
            return __o.address == self.address and __o.email == self.email and __o.port == self.port
        return False

    def __hash__(self):
        return hash((self.address, self.email, self.port))


def setup_argparse() -> str:
    """
    Configures argparse to accept path to files and returns the path.
    :return: path to the config file
    """

    def is_file(path: str) -> str:
        """
        Checks weather a given string is a valid path.
        :param path: path to a file
        :return: path if it is valid
        """

        if os.path.exists(path) and os.path.isfile(path):
            return path
        else:
            raise Exception("Provided path doesn\'t exists")

    # setup argparse and get path
    parser = argparse.ArgumentParser(
        description="a script, which draws for each user a secret santas and informs the santa which user it drew")
    parser.add_argument(
        "config_path",
        type=is_file,
        help="Path to the config json file, which stores the santas")
    args = parser.parse_args()
    path = args.config_path

    return path


def load_config(path: str) -> "dict[str, all]":
    """
    Loads a config file which must be given by the first argument,
    reads the file and parses it (must be json format).
    :return: dict containing the users
    """

    try:
        # read provided file
        with open(path, "r") as f:
            raw = f.read()
    except Exception as e:
        raise Exception(f"Unable to open and read {path}.")

    try:
        # parse to dict and interpret as json
        parsed = json.loads(raw)
    except Exception as e:
        raise Exception("The provided json file is not well formatted. Please see the README.md for more information.")

    # interpret as json
    return parsed


def extract_config(config: "dict") -> "tuple[Sender, list[SecretSanta]]":
    """
    Extracts the sender and the secret santas from the parsed file.
    Terminates if the input is invalid.
    :param config: parsed file
    :return: tuple containing a Sender object and a list of SecretSanta
    """

    try:
        # extract sender info and save as object in memory
        sender = Sender(
            address=config["sender"]["address"],
            email=config["sender"]["email"],
            port=config["sender"]["port"],
            subject=config["sender"]["subject"],
            body=config["sender"]["body"]
        )

        # extract santas
        santas = []
        for s in config["santas"]:
            santa = SecretSanta(
                s["name"],
                s["email"]
            )
            santas.append(santa)
    except Exception as e:
        raise Exception("The provided json file is not well formatted. Please see the README.md for more information.")

    # the minimal number of santas is two
    if len(santas) <= 1:
        raise Exception(f"Only {len(santas)} santa has been provided. "
                        "At least two santas have to play the game (but it starts to make sense with 3+ santas)")

    # checking, that the emails are unique and printing warnings, if at least one name is unique
    for i in range(len(santas)):
        for j in range(len(santas)):
            # skip entry's, where entries are equal
            if i == j:
                continue
            # check weather if emails is equal
            if santas[i].email == santas[j].email:
                raise Exception(f"The email {santas[i].email} has been referenced twice.")
            # check weather if usernames is equal
            if santas[i].name == santas[j].name:
                print(f"WARNING: The username \"{santas[i].name}\" has been used multiple times."
                      f"Please make sure, that none gets confused.")

    return sender, santas


def shuffle_santas(santas: list) -> "dict[SecretSanta, SecretSanta]":
    """
    Shuffles a list of santas, so that a santa did not draw itself.
    :param santas: list of santas
    :return: dictionary, where a santa references another santa
    """
    # shuffle santas
    random.shuffle(santas)

    # copy santas
    assigned_santas = santas.copy()

    s = assigned_santas.pop(0)
    assigned_santas.append(s)

    # convert assigned santas and other santas to dict
    santa_dict = {}
    for i in range(len(santas)):
        santa_dict[santas[i]] = assigned_santas[i]

    return santa_dict


def send_santa_invitations(sender: Sender, password: str, santas: "dict[SecretSanta, SecretSanta]") -> None:
    """
    Sends an email to every santa, with the name of the santa it drew.
    :param sender: sender object used for creating the server
    :param password: password used for authenticating the server
    :param santas: dict of santas, with reference which user it drew
    :return: None
    """

    def construct_message(santa: SecretSanta, recipient: SecretSanta, sender: Sender) -> EmailMessage:
        """
        Constructs a message to the recipient from the sender.
        The sender email address in the Header is changed to fit the theme.
        :param santa: santa, which drew the recipient
        :param recipient: recipient, which is being gifted by the santa
        :param sender: Sender object
        :return: Message object with RFC 5322 formatted header
        """

        def replace_reference(input: str, santa: SecretSanta, recipient: SecretSanta):
            """
            Replaces from an input string all occurrence of special codes (see README.md)
            :param input: the input string
            :param santa: Secret Santa, who has to gift someone
            :param recipient: Secret Santa, who is being gifted
            :return: input string, with the special codes being replaced with the according variables
            """

            output = input.replace("{santa.name}", santa.name)\
                .replace("{santa.email}", santa.email)\
                .replace("{recipient.name}", recipient.name)\
                .replace("{recipient.email}", recipient.email)

            return output

        subject = replace_reference(sender.subject, santa, recipient)
        body = replace_reference(sender.body, santa, recipient)

        message = EmailMessage(email.policy.SMTP)
        message["To"] = santa.email
        message["From"] = "santa.claus@north.pole"
        message["Subject"] = subject
        message["Date"] = email.utils.formatdate(localtime=True)
        message["Message-ID"] = email.utils.make_msgid()
        message.set_content(body)

        return message

    try:
        # Create a secure SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)

    except Exception as e:
        raise Exception("Coule not load protocol. Please enable/ install it.")

    try:
        # setup smtp for sending mails
        with smtplib.SMTP(sender.address, sender.port) as server:
            server.ehlo()

            # secure connection using starttls
            server.starttls(context=context)

            server.ehlo()

            # login to server
            server.login(sender.email, password)

            # send all mails to every santa
            for santa in santas:
                msg = construct_message(santa, santas[santa], sender)
                server.send_message(msg)

    except Exception as e:
        raise Exception("Error while sending at least one email.")


def main():
    try:
        print("Getting Arguments...")
        config_path = setup_argparse()
        print("Done\n")

        print("Parsing configuration...")
        config = load_config(config_path)
        print("Done\n")

        print("Extracting Santas...")
        sender, santas = extract_config(config)
        print("Done\n")

        print("Calculating Santas...")
        santas_assigned = shuffle_santas(santas)
        print("Done\n")

        # read the credentials for sending the emails
        password = getpass.getpass("Please enter the password for your email address: ")
        print()

        print("Sending email notifications...")
        send_santa_invitations(sender, password, santas_assigned)
        print("Done\n")

    except Exception as e:
        print("ERROR:", e, file=sys.stderr)


if __name__ == "__main__":
    main()
