import re
from random import random


def chat_tag(display_name):
    return "{:<5} >> ".format(display_name)


def normalize_text(text):
    """
    Remove all punctuation and lower the text. Also, strip whitespace off the ends of the text.

    Args:
        text (str): The text to be normalized.

    Returns:
        str: The normalized text.
    """

    return re.sub("[\W_]", "", text).lower().strip()


KEYBOARD = [['q', 'w', 'e,''r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm']]


def get_keyboard_neighbors(c):
    pass


def humanize_text(text):
    """
    Add some normal spelling mistakes to the text like:
    - Whitespace on wrong place
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
        if i == 0:
            continue

        # Shift the whitespace to the right
        if text[i] == " " and random() < 0.01:
            text_humanized = text_humanized[:-1] + " " + text_humanized[-1]
            i += 1
            continue

        # Swap letters. Note: Only letters 'inside' a word are considered
        if text[i-1] != " " and i < n-2 and text[i+2] != " " and random() < 0.01:
            text_humanized += text[i+1] + text[i]
            i += 2
            continue

        # Swap letter with letter close on keyboard
        if text[i] != " " and random() < 0.01:





