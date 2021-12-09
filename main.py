"""
links with infos to email sending:
    - https://realpython.com/python-send-email/
    - https://docs.python.org/3/library/email.examples.html
"""

import os
import sys
import ssl
import json
import getpass
import smtplib
import argparse

class SecretSanta:
    pass


def load_config() -> dict:
    """
    loads a config file from, which must be given by argument,
    reads the file and parses it as json
    :return: dict containing the users
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
    parser = argparse.ArgumentParser(description="a script, which calculates secret santas and informs the user via email")
    parser.add_argument("config_path", type=is_file,
                        help="Path to the config json file, which stores the santas")
    args = parser.parse_args()
    path = args.keylogfile

    # read provided file
    with open(path, "r") as f:
        raw = f.read()

    # interpret as json
    return json.loads(raw)


def check_input(config: dict):
    """
    checks weather the format of the loaded json is valid
    terminates the program and printing an error message, when the input was not valid.
    :param config: json pared file (dict)
    :return: None
    """
    pass


def extract_users(config: dict) -> list[SecretSanta]:
    """
    extracts the secret santas from the parsed file
    :param config: parsed file
    :return: list containing the santas
    """
    santas = []

    if 0:
        print("", file=sys.stderr)
        sys.exit(-1)

    return santas


def shuffle_santas(santas: list) -> dict[SecretSanta, SecretSanta]:
    """
    shuffles a list of santas, so that a santa did not draw itself
    :param santas: list of santas
    :return: dictionary, where a santa references another santa
    """

    pass


def send_santa_invitations(santas: dict[SecretSanta, SecretSanta]):
    """
    sends emails to every santa, with the address who it drew
    :param santas: list of santas
    :return:
    """

    pass


def main():
    config = load_config()

    check_input(config)

    santas = extract_users(config)

    santas = shuffle_santas(santas)

    # read the credentials for sending the emails
    send_email = input("Please enter your email:")
    password = getpass.getpass("Password for your email address")

    send_santa_invitations(send_email, password, santas)


if __name__ == "__main__":
    main()
