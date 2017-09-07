from config import PORT,  ROUTE_INBOX, ROUTE_CONNECT_INFO, DISPLAY_NAME_OTHER, DISPLAY_NAME_YOU
from helper import chat_tag
from http.client import HTTPConnection
import socket


def receive_message():
    """
    Receive message from the tester.

    Returns:
        str: The message from the tester.
    """

    return connection.getresponse().read().decode()


def send_chat_message(message):
    """
    Send a chat message to the tester

    Args:
        message:
    """

    connection.request('POST', ROUTE_INBOX, message)


def inform_about_connection():
    """
    Inform the tester about having connected.
    """

    connection.request('POST', ROUTE_CONNECT_INFO, socket.gethostbyname(socket.gethostname()))


if __name__ == '__main__':
    # Connect to the host
    host = input("Please provide the IP of the host (input nothing for localhost): ").strip()
    if not host:
        host = "localhost"
    connection = HTTPConnection(host, PORT)
    inform_about_connection()
    print(receive_message())

    # Start the chat
    while True:
        send_chat_message(input(chat_tag(DISPLAY_NAME_YOU)))
        print(chat_tag(DISPLAY_NAME_OTHER) + receive_message())
