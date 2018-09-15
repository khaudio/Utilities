#!/usr/bin/env python

from multiprocessing import Queue, Process
from threading import Thread
from serial import Serial, EIGHTBITS
import os
import time


class InvalidPortError(BaseException):
    pass


class CommBase:
    preamble, delimiter, escape = b'\x80', b'\x81', b'\x82'
    defaultPorts = {
            'Darwin': '/dev/cu.usbmodem144111',
            'Linux': '/dev/ttyACM0'
        }

    def __init__(self, port=None, baudrate=None, verbose=True):
        self.alive = True
        self.incoming, self.outgoing = Queue(), Queue()
        self.verbose = verbose
        self.port, self.baudrate = port, baudrate
        self.serial = Serial(
                port=self.port, baudrate=self.baudrate,
                bytesize=EIGHTBITS, timeout=1
            )
        self.procs = [
                Thread(target=self.read),
                Thread(target=self.__reader),
                Thread(target=self.__writer)
            ]
        for proc in self.procs:
            proc.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, val):
        if val is None:
            try:
                self.port = self.defaultPorts[os.uname().sysname]
            except:
                raise InvalidPortError('Invalid port')
        assert isinstance(val, str), 'Port must be str'
        self._port = val

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, val):
        if val is None:
            self.baudrate = 9600
        assert isinstance(val, int), 'Baudrate must be int'
        self._baudrate = val

    def close(self):
        self.alive = False
        for proc in self.procs:
            if isinstance(proc, Process):
                proc.terminate()
        for proc in self.procs:
            proc.join()
        self.serial.close()

    def join(self):
        """
        Method with no other purpose than to block
        This method is not required to be called.
        """
        while self.alive:
            try:
                pass
            except KeyboardInterrupt:
                break
            time.sleep(.0001)

    def __reader(self):
        """
        Read and decode messages from a serial device,
        then place them in a queue to be read from.
        """
        message, receiving = [], False
        while self.alive:
            data = self.serial.read()
            if data:
                if data == self.escape:
                    self.incoming.put(b''.join(message))
                    message, receiving = [], False
                elif data == self.preamble:
                    message, receiving = [], True
                elif receiving:
                    message.append(data)
            del data
            time.sleep(.0001)

    def __writer(self):
        """Writes messages from the outgoing queue to the serial port"""
        while self.alive:
            transmission = self.outgoing.get()
            self.serial.write(self.preamble + transmission + self.escape)

    def read(self):
        """Yields received serial messages from the queue"""
        while self.alive:
            message = self.incoming.get()
            try:
                payload = message.decode('utf-8')
            except:
                raise
            else:
                if self.verbose:
                    print(payload)
            yield message
            del message
            time.sleep(.0001)

    def write(self, message):
        """Non-blocking method to write serial messages"""
        transmission = b''
        if isinstance(message, (list, tuple)):
            transmission = bytearray(message)
        elif isinstance(message, str):
            transmission = bytes(message.encode('utf-8'))
        else:
            raise TypeError('Must be list, tuple, or str')
        self.outgoing.put(transmission)
