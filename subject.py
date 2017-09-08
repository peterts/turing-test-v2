from config import *
from helper import chat_tag, info_message, get_header
from http.client import HTTPConnection
import socket
import time
import sys


def connect_to_tester():
    """
    Connect to the tester

    Returns:
        HTTPConnection: A connection to the tester
    """

    while True:
        try:
            # Get the host
            host = input("Please provide the IP of the host (input nothing for localhost): ").strip()
            if not host:
                host = "localhost"

            # Connect
            print(info_message("Connecting to tester..."))
            connection = HTTPConnection(host, PORT)

            # Inform the tester about the connection
            connection.request('POST', ROUTE_CONNECT_INFO, socket.gethostbyname(socket.gethostname()))
            print(info_message(connection.getresponse().read().decode()))
            break
        except socket.gaierror:
            print(info_message("Invalid host '{}'".format(host)))

    return connection



class Subject:
    def __init__(self):
        """
        The Subject of the test.
        """

        self.connection = None

        # State of game
        self.n_questions_left = None
        self.points = None
        self.n_rounds = None

        # Commands
        self.commands = {
            "--help": self._display_help,
            "--questionsleft": self._display_questions_left,
            "--score": self._display_score,
            "--guess": self._make_guess,
            "--quit": self._quit
        }

    def _execute_command(self, command):
        """
        Execute the given command. Any message starting with double dashes (--) will be considered a command.

        Args:
            command (str): The command to be parsed

        Returns:
            bool: True if the command was '--guess', else False.
        """

        if command == '--guess':
            if self.n_questions_left == MAX_QUESTIONS:
                print(info_message("You need to ask at least one question before making a guess."))
                return False
            else:
                return True
        if command in self.commands:
            self.commands[command]()
        else:
            print(info_message("Invalid command '{}'".format(command)))
        return False

    def _start_new_game(self):
        """
        Start a new game.
        """

        self.n_rounds = 0
        self.points = 0

    def _start_new_round(self):
        """
        Start a new round.
        """

        self.n_questions_left = MAX_QUESTIONS
        self.n_rounds += 1
        print(info_message("Starting new round. Waiting for confirmation from tester..."))
        self.connection.request('POST', ROUTE_NEW_ROUND, "")
        print(info_message(self._receive_message()))

    def _receive_message(self):
        """
        Receive message from the tester.

        Returns:
            str: The message from the tester.
        """

        return self.connection.getresponse().read().decode()

    def _send_chat_message(self, message):
        """
        Send a chat message to the tester

        Args:
            message:
        """

        self.connection.request('POST', ROUTE_INBOX, message)

    def _display_help(self):
        """
        Display help for the game.
        """

        print(get_header())
        print("\n Welcome to the Turing Test.")
        print("\nRules:"
              "\n- The goal of this game is to guess whether the person you are talking with is a bot or not"
              "\n- Each round you have {} questions available to figure out what your conversation partner is"
              "\n- The fewer questions you use - the more points, but only if you guess correctly"
              "\n- When you are ready to guess, or have used all your questions, write '--guess' in the chat"
              "\n- Your points will be computed as: (n_correct * %questions_left_in_round * 100)/n_rounds".format(MAX_QUESTIONS))
        print("\nThe following commands are available during the game:")
        for k, v in self.commands.items():
            print("{:<20}{}".format(k, v.__doc__.strip()))
        print("\nNote: All text starting with double dashes (--) will be treated as commands."
              "\nAll other text will be treated as messages.\n")

    def _update_points(self):
        """
        Add points. Should only be done for correct guesses
        """

        self.points += 100 * (self.n_questions_left + 1) / MAX_QUESTIONS

    def _compute_score(self):
        """
        Compute the score based on the points, and number of rounds played.
        """

        return self.points / self.n_rounds

    def _make_guess(self):
        """
        Guess whether the tester is a bot or a human.
        """

        guess_tester_type = input("What do you think the tester is ({}/{}): ".format(TESTER_BOT, TESTER_HUMAN))
        while guess_tester_type not in [TESTER_HUMAN, TESTER_BOT]:
            guess_tester_type = input("{} is not a valid tester type, select either {} or {}: ".format(guess_tester_type, TESTER_BOT, TESTER_HUMAN))

        print(info_message("You guessed {}. Waiting for response...".format(guess_tester_type)))
        self.connection.request('POST', ROUTE_CHECK_GUESS, guess_tester_type)
        result = self._receive_message()

        time.sleep(1)
        if result == GUESS_CORRECT:
            print(info_message("Your guess was correct!"))
            self._update_points()
        else:
            print(info_message("Your guess was wrong..."))
        self._display_score()

    def _display_questions_left(self):
        """
        Display the number of questions left in the current round.
        """

        print(info_message("Number of questions left in this round: " + str(self.n_questions_left)))

    def _display_score(self):
        """
        Display the current points for the game.
        """

        print(info_message("Current score: " + str(self._compute_score())))

    def _quit(self):
        """
        End the game.
        """

        print(info_message("Game ended"))
        sys.exit(0)

    def run(self):
        """
        Run the test.
        """
        self.connection = connect_to_tester()

        # Start new game
        while True:
            self._start_new_game()
            self._display_help()
            # Start new round
            while True:
                self._start_new_round()
                while self.n_questions_left > 0:
                    # Read message
                    message = input(chat_tag(DISPLAY_NAME_YOU))

                    # Check if the message is a command
                    if message[:2] == "--":
                        command_was_guess = self._execute_command(message)
                        if command_was_guess:
                            break
                    # Else, send the message to the tester
                    else:
                        self._send_chat_message(message)
                        print(chat_tag(DISPLAY_NAME_OTHER) + self._receive_message())
                        self.n_questions_left -= 1
                if self.n_questions_left == 0:
                    print(info_message("No questions left. Yoy now need to make a guess."))
                self._make_guess()
                if 'y' not in input("Start new round (y/N): "):
                    break

            print(info_message("Game ended. Your final score is: {} out of 100".format(self._compute_score())))
            self.connection.request('POST', ROUTE_ENDED_GAME, "")
            self._receive_message()
            if 'y' not in input("Start new game (y/N): "):
                break


if __name__ == '__main__':
    subject = Subject()
    subject.run()