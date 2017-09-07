from bottle import run, post, request
from config import PORT,  ROUTE_INBOX, ROUTE_CONNECT_INFO, DISPLAY_NAME_OTHER, DISPLAY_NAME_YOU
from helper import chat_tag
from cleverwrap import CleverWrap
import os
import sys


CLEVERBOT_API_KEY_VAR = "CLEVERBOT_API_KEY"


@post(ROUTE_INBOX)
def receive_and_send_message():
    message_received = request.body.read().decode()
    print(chat_tag(DISPLAY_NAME_OTHER) + message_received)
    return cw.say(message_received)


@post(ROUTE_CONNECT_INFO)
def has_connected():
    host = request.body.read().decode()
    print("Host {} just connected".format(host))
    return "Successfully connected"


if __name__ == '__main__':
    # Connect to cleverbot
    if CLEVERBOT_API_KEY_VAR in os.environ:
        cw = CleverWrap(os.environ[CLEVERBOT_API_KEY_VAR])
    else:
        print("No cleverbot API key found. Please do the following to get up and running:"
              "- Register a user at 'https://www.cleverbot.com/api/'"
              "- Set the environment variable '{}' to the API key value given on your cleverbot api account page.")
        sys.exit(1)

    # Start bottle server
    run(host='localhost', port=PORT, quiet=True)
