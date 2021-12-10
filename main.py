"""
links with infos to email sending:
    - https://realpython.com/python-send-email/
    - https://docs.python.org/3/library/email.examples.html
"""

import os
import sys
import ssl
import json
import random
import getpass
import smtplib
import argparse


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


class Sender:
    address: str  # address of the sender server
    email: str    # email address, from which messages are beeing send
    port: int     # port, on which the server should listen

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


def setup_argparse():
    """
    todo
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
            raise str

    # setup argparse and get keylog path
    parser = argparse.ArgumentParser(description="a script, which draws for each user a secret santas"
                                                 " and informs the santa which user it drew")
    parser.add_argument("config_path", type=is_file,
                        help="Path to the config json file, which stores the santas")
    args = parser.parse_args()
    path = args.config_path


def load_config(path: str) -> "dict[str, all]":
    """
    loads a config file from, which must be given by argument,
    reads the file and parses it as json
    :return: dict containing the users
    """

    # read provided file
    with open(path, "r") as f:
        raw = f.read()

    # interpret as json
    return json.loads(raw)


def extract_users(config: "dict") -> "list[SecretSanta]":
    """
    extracts the secret santas from the parsed file.
    Terminates if the input is invalid
    :param config: parsed file
    :return: list containing the santas
    """
    
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
    
    # todo check, that no email and name are equal

    # Raise an error, when the input is invalid formatted
    if 0:
        print("", file=sys.stderr)
        raise "InvalidInputError()"

    return sender, santas


def shuffle_santas(santas: list) -> "dict[SecretSanta, SecretSanta]":
    """
    Shuffles a list of santas, so that a santa did not draw itself
    :param santas: list of santas
    :return: dictionary, where a santa references another santa
    """
    
    def constraint(key_santas: "list[SecretSanta]", value_santas: "list[SecretSanta]") -> bool:
        """
        Checks that in two given lists no equal values have the same index:
        fisrt_arr[i] != second_arr[i]
        """
        
        for i in range(len(key_santas)):
            if key_santas[i] == value_santas[i]:
                return False
        return True

    # setup assigned santas
    assigned_santas: santas.copy()
    
    # shuffle the santas until no equal santas share the same index
    while not constraint(santas, assigned_santas):
        random.shuffle(assigned_santas)
    
    # convert assigned santas and other santas to dict
    santa_dict = {}
    for i in range(len(santas)):
        santa_dict[santas[i]] = assigned_santas[i]
        
    return santa_dict


def send_santa_invitations(santas: "dict[SecretSanta, SecretSanta]", sender_config: dict, password: str):
    """
    Sends an email to every santa, with the name of the santa it drew
    :param santas: list of santas
    :return: None
    """

    # todo
    def construct_message(recipiant: SecretSanta, sender: SecretSanta):
        return "Subject: {recipiant.name}\n\nTest Message, your sender is {sender.name}"

    # Create a secure SSL context
    context = ssl.create_default_context()

    # todo
    with smtplib.SMTP_SSL(sender_config["address"], sender_config["port"], context=context) as server:        
        # login to server
        server.login(sender_config["email"], password)
        
        # send all mails to the santas
        for santa in santas:
            server.sendmail(sender_config["email"], santa.email, construct_message(santas[santa], santa))


def main():
    config_path = setup_argparse()
    
    config = load_config(config_path)

    sender, santas = extract_users(config)
    
    santas = shuffle_santas(santas)

    for s in santas:
        print(s, s[s])

    # read the credentials for sending the emails
    # password = getpass.getpass("Password for your email address")

    send_santa_invitations(sender, password, santas)


if __name__ == "__main__":
    main()
