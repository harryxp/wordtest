#!/usr/bin/python

import curses
import datetime as dt
import functools
import random
import subprocess
import sys

def main_loop(words, stdscr):
    stdscr.addstr('Loading file(s) %s...\n' % words.get_input_files())
    stdscr.addstr(
"""
Usage:
    <SPACE> - skip to the next word
    </>     - look it up in the dictionary
    <q>     - quit

Now press <SPACE> to continue...
"""
    )

    # the "event loop"
    while True:
        try:
            input = stdscr.getkey()

            if input == ' ':
                next_word = words.get_next_word()
                if next_word:
                    current_word = next_word
                else:
                    return
                stdscr.clear()
                stdscr.addstr(current_word)
            elif input == '/':
                if 'current_word' in locals():
                    subprocess.call(['open', 'dict://%s' % current_word])
                    words.save_word(current_word)
            elif input == 'q':
                return
        except curses.error:
            # keys with no input
            continue

class Words(object):
    def __init__(self):
        self.input_files = []
        self.word_list = []
        self.saved_word_list = []
        self.reviewed_word_count = 0
    def get_next_word(self):
        if not self.is_empty():
            index = random.randint(0, len(self.word_list)-1)
            w = self.word_list[index]
            self.word_list.remove(w)
            self.reviewed_word_count += 1
            return w
    def add_file(self, f):
        self.input_files.append(f)
    def get_input_files(self):
        return ', '.join(self.input_files)
    def add_word(self, w):
        self.word_list.append(w)
    def is_empty(self):
        return not self.word_list
    def save_word(self, w):
        if not self.saved_word_list or self.saved_word_list[-1] != w:
            self.saved_word_list.append(w)
    def save_file(self):
        if self.saved_word_list:
            fn = 'wordlist_%s.txt' % dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            fh = open(fn, 'w')
            self.saved_word_list.sort()
            for w in self.saved_word_list:
                fh.write(w)
                fh.write('\n')
            fh.close()
            return fn

if __name__ == '__main__':
    words = Words()
    for word_file in sys.argv[1:]:
        fh = open(word_file, 'r');
        words.add_file(word_file)
        for line in fh:
            w = line.rstrip('\n')
            words.add_word(w)
        fh.close()
    if words.is_empty():
        print('Please provide word file(s).')
        exit(1)

    curses.wrapper(functools.partial(main_loop, words))
    fn = words.save_file()
    print('You have reviewed %d word(s).' % words.reviewed_word_count)
    if fn:
        print('You have saved %d word(s) in %s'
                % (len(words.saved_word_list), fn))

