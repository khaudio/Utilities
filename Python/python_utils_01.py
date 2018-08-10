#!/usr/bin/env python

"""
Code stored for re-use
"""

from threading import Thread
from multiprocessing import Queue
from serial import Serial, EIGHTBITS
from sys import _getframe
import asyncio


def from_coroutine():
    return _getframe(2).f_code.co_flags & 0x380


def is_async():
    """Determine whether this function was invoked by a coroutine"""
    if from_coroutine(): # called by a coroutine
        pass
    else: # called by a function
        pass


# Create and start a function and non-blocking thread with multiple operations
def do_thread(x=1):
    Thread(target=lambda: (x * 1, x + 3, x - 6)).start()


class CommBase:
    def __init__(self, port=None, baud=None):
        self.alive, self.received  = True, Queue()
        self.preamble, self.escape = '\x3C', '\x0A'
        self.serial = Serial(
            port = '/dev/ttyACM0' if port is None else port,
            baudrate = 9600 if baud is None else baud,
            bytesize = EIGHTBITS,
            timeout = 1
            )
        self.reader = Process(target=self.read_from_serial)
        self.listener = Process(target=self.listen)
        for proc in (self.reader, self.listener):
            proc.start()

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.alive = False
        for proc in (self.reader, self.listener):
            proc.terminate()
            proc.join()
        self.serial.close()

    def run(self):
        while self.alive:
            try:
                pass
            except KeyboardInterrupt:
                break
            sleep(.0001)

    def listen(self):
        """Process serial messages"""
        while self.alive:
            message = self.received.get()
            payload = b''.join(message).decode('ascii')
            print(payload)
            del message, payload

    def read_from_serial(self):
        """Read messages from a serial device"""
        message, incoming = [], False
        while self.alive:
            data = self.serial.read()
            if data:
                if not incoming:
                    if data == self.preamble:
                        incoming = True
                        message = []
                elif incoming:
                    if data == self.escape:
                        yield message
                        self.received.put(message)
                        incoming = False
                    else:
                        message.append(data)
            del data

    def write_to_serial(self, command, length=0):
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
            self.serial.write(command)
        else:
            raise TypeError('Command must be of type list, string, or bytes')
        if transmission:
            self.serial.write(self.preamble + transmission + self.escape)


class AsyncBase:
    """Abstracts asyncio usage so less boilerplate code is required"""
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.coroutines = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.close()

    def add_tasks(self, *coroutines):
        """Adds one or more coroutines, but does not execute them"""
        for coroutine in coroutines:
            self.coroutines.append(asyncio.ensure_future(coroutine))

    def do_tasks(self):
        """Executes async coroutines"""
        self.loop.run_until_complete(asyncio.gather(*self.coroutines))


class ExampleAsync(AsyncBase):
    """Example class for demonstrating abstracted async task execution"""
    async def hello(self, place):
        """Example async coroutine"""
        print('Hello')
        await asyncio.sleep(0)
        print(place)

    async def goodbye(self, place):
        """Example async coroutine"""
        print('Goodbye')
        await asyncio.sleep(0)
        print(place)


def round_down(num, decimalPlaces=0):
    """Rounds down to a chosen decimal place"""
    multiplied = 10 ** decimalPlaces
    return floor(num * multiplied) / multiplied


def special_text(text, effect='grey', percentage=False):
    """
    Adds effects to print output.
    Positive numbers are green, negative numbers are red, unless overridden.
    """
    effects = {
            'red': '\033[91m', 'grey': '\033[0m', 'green': '\033[92m',
            'yellow': '\033[93m', 'purple': '\033[95m', 'bold': '\033[1m'
        }
    if isinstance(text, (int, float)) and effect is 'grey':
        if text > 0:
            effect = 'green'
        elif text < 0:
            effect = 'red'
        text = str(text)
        if percentage:
            text += ' %'
    return ''.join(effects[effect], text, effects['grey'])


def random_data(x, percentChange):
    """Generate random shifts within specified percentage range"""
    for i in range(x):
        shift = randint(0, (percentChange * 1000)) / 100000
        direction = randrange(0, 2, 1)
        if direction is 1:
            yield shift
        else:
            yield (shift * (-1))


if __name__ == '__main__':
    places = ('Home', 'Valhalla', 'World')
    with ExampleAsync() as example:
        for place in places:
            example.add_tasks(example.hello(place), example.goodbye(place))
        example.do_tasks()
