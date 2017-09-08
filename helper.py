import re
from random import random


def chat_tag(display_name):
    return "{:<5} >> ".format(display_name)


def info_message(message):
    return "INFO: " + message


def normalize_text(text):
    """
    Remove all punctuation and lower the text. Also, strip whitespace off the ends of the text.

    Args:
        text (str): The text to be normalized.

    Returns:
        str: The normalized text.
    """

    return re.sub("([^\w\s]|_)", "", text).lower().strip()


KEYBOARD = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm']]


def get_keyboard_neighbors(c):
    for keyboard_row in KEYBOARD:
        for j, k in enumerate(keyboard_row):
            if c != k:
                continue
            neighbors = []
            if j > 0:
                neighbors.append(keyboard_row[j-1])
            if j < len(keyboard_row) - 1:
                neighbors.append(keyboard_row[j+1])
            return neighbors
    return []


def humanize_text(text):
    """
    Add some normal spelling mistakes to the text like:
    - Letters swapped
    - Letters replaced with neighboring keyboard letter

    Args:
        text (str): The text to be humanized.

    Returns:
        str: The humanized text.
    """

    text_humanized = ""
    i, n = 0, len(text)
    while i < n:
        if i > 0:
            # Swap letters. Note: Only letters 'inside' a word are considered
            if i < n - 2 and random() < 0.005:
                text_humanized += text[i+1] + text[i]
                i += 2
                continue

            # Swap letter with letter close on keyboard
            if text[i] != " " and random() < 0.005:
                keyboard_neighbors = get_keyboard_neighbors(text[i])
                if len(keyboard_neighbors) == 1 or random() < 0.5:
                    text_humanized += keyboard_neighbors[0]
                else:
                    text_humanized += keyboard_neighbors[1]
                i += 1
                continue

        text_humanized += text[i]
        i += 1
    return text_humanized


def get_header():
    header = """
      ______           _                ______          __ 
     /_  __/_  _______(_)___  ____ _   /_  __/__  _____/ /_
      / / / / / / ___/ / __ \/ __ `/    / / / _ \/ ___/ __/
     / / / /_/ / /  / / / / / /_/ /    / / /  __(__  ) /_  
    /_/  \__,_/_/  /_/_/ /_/\__, /    /_/  \___/____/\__/  
                           /____/                          
    By Peter Sandberg
    """
    return header


def get_chat_line_separator():
    return "-"*70




