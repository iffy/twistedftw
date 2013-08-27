#!/usr/bin/env python
# guessinggame.py
# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
import random

def main(min_val, max_val):
    the_number = random.randint(min_val, max_val)
    guess = None
    guesses = 0
    while guess != the_number:
        try:
            guess = int(raw_input('Guess the number %s to %s:\n' % (min_val, max_val)))
            guesses += 1
        except:
            print 'not a number!'
            continue
        if guess > the_number:
            print 'too high'
        elif guess < the_number:
            print 'too low'
    print 'Yep, it was %d.  You got it in %d guesses.' % (the_number, guesses)


if __name__ == '__main__':
    main(1, 10)