#!/usr/bin/env python

"""
Code stored for re-use
"""

from threading import Thread
from multiprocessing import Queue
from serial import Serial, EIGHTBITS
import asyncio


# Create and start a function and thread with multiple operations
x = 1
t = Thread(target=lambda: (x * 1, x + 3, x - 6)).start()


class CommBase(object):
    def __init__(self, port=None, baud=None):
        self.alive, self.preamble, self.escape, self.received = True, '\x3C', '\x0A', Queue()
        self.serial = Serial(
            port = '/dev/ttyACM0' if port is None else port,
            baudrate = 9600 if baud is None else baud,
            bytesize = EIGHTBITS,
            timeout = 1
            )
        self.reader = Process(target=self.read_from_serial)
        self.listener = Process(target=self.listen)
        for proc in [self.reader, self.listener]:
            proc.start()


    def __enter__(self):
        return self


    def __exit__(self, a, b, c):
        self.alive = False
        map(lambda proc: (proc.terminate(), proc.join()), (self.reader, self.listener))
        self.serial.close()


    def run(self):
        while True:
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


class ExampleAsync(object):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.places = set()


    def __enter__(self):
        return self


    def __exit__(self, a, b, c):
        self.loop.close()


    def add(self, *places):
        for place in places:
            assert isinstance(place, str), 'Must be str'
            self.places.add(place)


    def start(self):
        """Start the event loop to run the coroutines"""
        coroutines = []
        for place in self.places:
            coroutines.extend([
                asyncio.ensure_future(self.hello(place)),
                asyncio.ensure_future(self.goodbye(place))
                ])
        self.loop.run_until_complete(asyncio.gather(*coroutines))


    async def hello(self, place):
        """Example async coroutine"""
        print('Hello')
        await asyncio.sleep(.4)
        print(place)


    async def goodbye(self, place):
        """Example async coroutine"""
        print('Goodbye')
        await asyncio.sleep(1.3)
        print(place)


def round_down(amount, decimalPlaces=0):
    """Round down a chosen decimal place"""
    multiplied = 10 ** decimalPlaces
    return floor(amount * multiplied) / multiplied


def special_text(text, effect='grey', percentage=False):
    """
    Adds effects to print output.
    Positive numbers are green, negative numbers are red, unless overridden.
    """
    effects = {'red': '\033[91m', 'grey': '\033[0m', 'green': '\033[92m',
               'yellow': '\033[93m', 'purple': '\033[95m', 'bold': '\033[1m'}
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
    places = ('home', 'valhalla', 'world')
    with ExampleAsync() as e:
        e.add(*places)
        e.start()
