#!/usr/bin/env python

"""
Code stored for re-use
"""

from threading import Thread
from multiprocessing import Queue


# Multiple operations in one lambda
lambda x: (x * 1, x + 3, x - 6)


# Create a and start a function and thread in one line
Thread(target=lambda x: x + 1).start()


def listen():
    """Process serial messages"""
    while True:
        for message in read_from_serial():
            payload = b''.join(data).decode('ascii')
            print(payload)
        sleep(.0001)


def read_from_serial(q=None, preamble='\x3C', escape='\x0A'):
    """Read messages from a serial device"""
    message, incoming = [], False
    while True:
        data = serial.read()
        if data:
            if not incoming:
                if data == preamble:
                    incoming = True
                    message = []
            elif incoming:
                if data == escape:
                    yield message
                    if q:
                        q.put(message)
                    incoming = False
                else:
                    message.append(data)
        del data
        sleep(.0001)
    serial.close()


def write_to_serial(command, length=0, preamble='\x3C', escape='\x0A'):
    """Write messages to a serial device"""
    transmission = b''
    if isinstance(command, list) and length:
        if len(command) == length:
            transmission = bytearray(command)
        else:
            raise ValueError(f'Command length must be {length}')
    elif isinstance(command, str):
        transmission = bytes(command.encode('utf-8'))
    elif isinstance(command, bytes):
        serial.write(command)
    else:
        raise TypeError('Command must be of type list, string, or bytes')
    if transmission:
        serial.write(preamble + transmission + escape)


def round_down(amount):
    """Round down the 9th decimal place"""
    return (floor(amount * 100000000) / 100000000)


def special_text(text, effect='grey', percentage=False):
    """
    Adds effects to print output.
    Positive numbers are green, negative numbers are red, unless overridden.
    """
    effects = {'red': '\033[91m',
               'grey': '\033[0m',
               'green': '\033[92m',
               'yellow': '\033[93m',
               'purple': '\033[95m',
               'bold': '\033[1m'}
    if text.isdigit() and effect is 'grey':
        if text > 0:
            effect = 'green'
        elif text < 0:
            effect = 'red'
        text = str(text)
        if percentage:
            text = text + ' %'
    return effects[effect] + text + effects['grey']


def random_data(x, percentChange):
    """Generate random shifts within specified percentage range"""
    for i in range(x):
        shift = randint(0, (percentChange * 1000)) / 100000
        direction = randrange(0, 2, 1)
        if direction is 1:
            yield shift
        else:
            yield (shift * (-1))
