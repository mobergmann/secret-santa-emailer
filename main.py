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
    address: str  # address of the sender server
    email: str  # email address, from which messages are beeing send
    port: int  # port, on which the server should listen

    def __init__(self, address, email, port) -> None:
        self.address = address
        self.email = email
        self.port = port

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


def extract_users(config: "dict") -> "tuple[Sender, list[SecretSanta]]":
    """
    Extracts the secret santas from the parsed file.
    Terminates if the input is invalid.
    :param config: parsed file
    :return: list containing the santas
    """

    try:
        # extract sender info and save as object in memory
        sender = Sender(
            address=config["sender"]["address"],
            email=config["sender"]["email"],
            port=config["sender"]["port"]
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

    def constraint(key_santas: "list[SecretSanta]", value_santas: "list[SecretSanta]") -> bool:
        """
        Checks that in two given lists no equal values have the same index:
        first_arr[i] != second_arr[i]
        """

        for i in range(len(key_santas)):
            if key_santas[i] == value_santas[i]:
                return False
        return True

    # setup assigned santas
    assigned_santas = santas.copy()

    # shuffle the santas until no equal santas share the same index
    while not constraint(santas, assigned_santas):
        random.shuffle(assigned_santas)

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

    def construct_message(recipient: SecretSanta, sender: SecretSanta):
        """
        Constructs a message to the recipient from the sender.
        The sender email address in the Header is changed to fit the theme.
        :param recipient: email recipient
        :param sender: email account, from which the emails are being send
        :return:
        """

        message = EmailMessage(email.policy.SMTP)
        message["To"] = recipient.email
        message["From"] = "santa.claus@north.pole"
        message["Subject"] = "The Secret Santas were drawn!"
        message["Date"] = email.utils.formatdate(localtime=True)
        message["Message-ID"] = email.utils.make_msgid()
        message.set_content(f"You ({sender.name}) have to gift {recipient.name}")

        return message

    try:
        # Create a secure SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)

    except Exception as e:
        raise Exception("Coule not load protocol. Please enable it.")

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
                msg = construct_message(santas[santa], santa)
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
        sender, santas = extract_users(config)
        print("Done\n")

        print("Calculating Santas...")
        santas = shuffle_santas(santas)
        print("Done\n")

        # read the credentials for sending the emails
        password = getpass.getpass("Please enter the password for your email address: ")

        print("Sending email notifications...")
        send_santa_invitations(sender, password, santas)
        print("Done\n")

    except Exception as e:
        print("ERROR:", e, file=sys.stderr)


if __name__ == "__main__":
    main()
