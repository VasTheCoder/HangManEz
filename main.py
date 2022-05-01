from random import randint
import curses
from re import finditer
import sys
from typing import Optional
from nltk.corpus import wordnet

from hangmen import art

TOTAL_WORDS = 852
DEBUG = False
CHANCES = len(art)


class GameLost(Exception):
    pass


class HangManPicture:
    def __init__(self) -> None:
        self.chance = 0
        self.as_string = art[self.chance]

    def add_body_part(self) -> None:
        'add a body part if user is wrong'
        self.chance += 1
        if self.chance >= CHANCES - 1:
            raise GameLost
        self.as_string = art[self.chance]


class HangManWord:
    def __init__(self, word: str, picture: HangManPicture) -> None:
        self.word: str = word
        self.hangmanpic = picture
        self.found = ['_'] * len(self.word)
        self.as_str: str = ' '.join(self.found)
        self.chances = CHANCES

    def guess_letter(self, letter: str) -> bool:
        'check if letter is correct and update accordingly'
        if letter not in self.word:
            self.hangmanpic.add_body_part()
            self.chances -= 1
            return False

        # All occurences of letter
        idxes = [_.start() for _ in finditer(letter, self.word)]
        for idx in idxes:
            self.found[idx] = letter
            self.as_str: str = ' '.join(self.found)
        return True

    def __str__(self) -> str:
        return self.word


def play(stdscr) -> tuple[str, bool]:
    'play the game and return the correct word along with if the user won or not'
    hangman = HangManPicture()
    if DEBUG:
        answer = 'FIGHT'
    else:
        answer = generate_word().upper()
    word = HangManWord(answer, hangman)
    current_letter = " "
    while True:
        stdscr.clear()

        print_instructions(stdscr, word)
        print_definition(stdscr, str(word), 2)
        stdscr.addstr(3, 3, hangman.as_string)
        try:
            temp = handle_input(stdscr, word, current_letter)
        except GameLost:
            return answer, False

        if ''.join(word.found) == str(word):
            stdscr.refresh()
            break

        if temp is not None:
            current_letter = temp
        stdscr.refresh()
    return answer, True


def handle_input(stdscr, word: HangManWord, current_letter: str) -> Optional[str]:
    '''get a key from the user and do the appropriate action
        returns uppercase key if keypressed was alphabet else returns None
    '''
    stdscr.addstr(11, 13, current_letter)
    key = get_key_or_exit(stdscr)
    if key == 10:  # If key pressed was Enter
        word.guess_letter(current_letter)
        return

    if not ((65 <= key <= 90) or (97 <= key <= 122)):
        # If keypressed was not alphabet
        return
    if (97 <= key <= 122):
        # If key was lowercase
        key -= 32  # turn key uppercase

    current_letter = chr(key)
    return current_letter


def get_key_or_exit(stdscr) -> int:
    'get a key, exit if key is escape'
    key = stdscr.getch()
    # print(key)
    if key == 27:
        sys.exit()
    return key


def start_screen(stdscr) -> None:
    'add the start screen to the window'
    stdscr.addstr(1, 0, 'Welcome to My Hangman Game')
    stdscr.addstr(2, 0, 'Press Any key to continue')
    stdscr.getkey()


def print_instructions(stdscr, word: HangManWord) -> None:
    'print the instructions and the information the user needs to know'
    stdscr.addstr(0, 0, 'Type a letter then press Enter to confirm')
    stdscr.addstr(1, 0, 'Definition:')
    stdscr.addstr(11, 0, 'Your guess:')
    stdscr.addstr(12, 0, word.as_str)
    stdscr.addstr(13, 0, f'Chances left: {word.chances}')


def print_definition(stdscr, word: str, column: int) -> None:
    'print the definiton to stdscr on specified column'
    definition = get_definition(word)
    stdscr.addstr(column, 2, definition)


def generate_word() -> str:
    'generate a random word from words.txt'
    with open('words.txt', 'r', encoding='UTF-8') as file_:
        words = file_.readlines()
        index = randint(0, TOTAL_WORDS-1)
        word = words[index][:-1]
        return word


def get_definition(word: str) -> str:
    syns = wordnet.synsets(word)
    return syns[0].definition()


def main(stdscr):
    while True:
        answer, won = play(stdscr)
        if won:
            stdscr.addstr(11, 0, "Wohoo! the answer is right!")
        else:
            stdscr.addstr(11, 0, "Oh No! You lost")
        stdscr.addstr(12, 0, f'The answer was {answer}')
        stdscr.addstr(13, 0, 'Press any key to contiue, escape to exit')
        get_key_or_exit(stdscr)


curses.wrapper(main)  # type: ignore
