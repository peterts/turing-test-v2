from bottle import Bottle, request
from config import *
from helper import chat_tag, info_message, normalize_text, humanize_text
from cleverwrap import CleverWrap
import os
from time import time, sleep
from random import random
import socket


CLEVERBOT_API_KEY_VAR = "CLEVERBOT_API_KEY"


def connect_to_cleverbot():
    """
    Connect to the Cleverbot API.

    Returns:
        CleverWrap: The connection to the Cleverbot API
    """

    if CLEVERBOT_API_KEY_VAR in os.environ:
        return CleverWrap(os.environ[CLEVERBOT_API_KEY_VAR])
    raise EnvironmentError(
        "\n\nNo cleverbot API key found. Please do the following to get up and running:"
        "\n- Register a user at 'https://www.cleverbot.com/api/'"
        "\n- Set the environment variable '{}' to the API key value given on your cleverbot api account page.".format(CLEVERBOT_API_KEY_VAR))


def estimate_writing_speed():
    """
    Estimate the writing speed of the human tester.

    Returns:
        float: The estimated writing speed in characters/sec
    """

    n = 3
    print(info_message("Starting estimation of writing speed"))
    print("Please write {} arbitrary sentences. End each sentence with enter.".format(n))
    speeds = []
    for i in range(n):
        t_start = time()
        text = input("Sentence {}: ".format(i+1))
        speeds.append((time()-t_start)/len(text))
    return sum(speeds)/n


class Tester(Bottle):
    def __init__(self):
        """
        Used to host a Turing Test.
        """

        super(Tester, self).__init__()

        # Connect to the bot
        self.bot = connect_to_cleverbot()
        print(info_message("Successfully connected to cleverbot"))

        # Set up the routes.
        self.route(ROUTE_INBOX, method='POST', callback=self.receive_and_send_message)
        self.route(ROUTE_CONNECT_INFO, method='POST', callback=self.has_connected)
        self.route(ROUTE_NEW_ROUND, method='POST', callback=self.start_new_round)
        self.route(ROUTE_CHECK_GUESS, method='POST', callback=self.check_guess)
        self.route(ROUTE_ENDED_GAME, method='POST', callback=self.game_ended)

        # Initalized later
        self.tester_type = None

        # Estimate writing speed
        # If false, a random writing speed will be chosen
        # The writing speed is in chars/sec
        if 'y' in input("Estimate writing speed (y/N): "):
            self.writing_speed = estimate_writing_speed()
        else:
            self.writing_speed = 0.15 + random() * 0.2
        print(info_message("Writing speed estimated to {:.3f} characters/sec".format(self.writing_speed)))

    def start_new_round(self):
        """
        Start a new round. For the round to be started, you need to select whether you our the bot is answering.

        Returns:
            str: Confirmation message.
        """

        # Get the tester type
        print(info_message("New round started by the user."))
        tester_type = input("Will the bot or you be answering the questions ({}/{}): ".format(TESTER_BOT, TESTER_HUMAN))
        while tester_type not in [TESTER_HUMAN, TESTER_BOT]:
            tester_type = input("'{}' is not a valid tester type, select either {} or {}: ".format(tester_type, TESTER_BOT, TESTER_HUMAN))

        if tester_type == TESTER_BOT:
            print(info_message("The bot will be answering the questions. Sit back and relax!"))
        if tester_type == TESTER_HUMAN:
            print(info_message("You will be answering the questions. Good luck."))
        print(info_message("Waiting for first message..."))

        self.tester_type = tester_type

        # Reset the bot
        self.bot.reset()

        return "New round ready"

    def game_ended(self):
        """
        Inform the tester that the previous game was ended.
        """
        print(info_message("Current game ended. Waiting for new game to start..."))
        return "Ok"

    def check_guess(self):
        """
        Check the guess made by the subject.

        Returns:
            str: Whether or not the result was correct.
        """

        guess_tester_type =  request.body.read().decode()
        print(info_message("The human guess that you're a {}".format(guess_tester_type)))
        print(info_message("Waiting for a new round to start..."))
        if guess_tester_type == self.tester_type:
            return GUESS_CORRECT
        return GUESS_WRONG

    def receive_and_send_message(self):
        """
        Receive a message from the subject. If tester_type=bot, the bot will answer the question. If tester_type=human,
        you will be answering the questions.

        Returns:
            str: The reply.
        """

        message_received = request.body.read().decode()
        print(chat_tag(DISPLAY_NAME_OTHER) + message_received)

        # Get reply for the message
        # Bot answers the message
        if self.tester_type == TESTER_BOT:
            # Get the reply from the bot
            t_start = time()
            bot_reply = self.bot.say(message_received)
            t = time() - t_start

            # Normalize and humanize the text
            bot_reply = humanize_text(normalize_text(bot_reply))

            # Add a delay to the message sending in case the bot responded
            # too fast
            estimated_writing_time = len(bot_reply) * self.writing_speed
            if t < estimated_writing_time:
                sleep(estimated_writing_time-t)

            print(chat_tag(DISPLAY_NAME_YOU) + bot_reply)
            return bot_reply

        # You answer the message
        return normalize_text(input(chat_tag(DISPLAY_NAME_YOU)))

    def has_connected(self):
        """
        Get notified that the user has connected.

        Returns:
            str: Confirmation.
        """

        host = request.body.read().decode()
        print(info_message("Host {} just connected".format(host)))
        return "Successfully connected"


if __name__ == '__main__':
    tester = Tester()
    print(info_message("Starting Turning Test Server on {}".format(socket.gethostbyname(socket.gethostname()))))
    print(info_message("Waiting for connection from subject..."))
    tester.run(host='localhost', port=PORT, quiet=True)
