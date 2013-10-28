#! /usr/bin/env python

import argparse
import logging
import socket

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

class Pybot(object):

    def __init__(self, server, port, nick, nickserv, password, channels):
        self.server = server
        self.port = port
        self.nick = nick
        self.nickserv = nickserv
        self.password = password
        self.channels = channels

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server, self.port))
        self.send('USER %s %s %s %s' % (self.nick, self.nick,
                                        self.nick, self.nick))
        self.send('NICK %s' % self.nick)
        if self.password != '':
            self.send('PRIVMSG %s : IDENTIFY %s' %
                      (self.nickserv, self.password))
        for channel in self.channels:
            self.send('JOIN %s' % channel)
        self.listen()

    def listen(self):
        buff = ''
        while True:
            raw_data = self.socket.recv(2048)
            msg_chunks = raw_data.split('\n')

            if buff:
                msg_chunks[0] = buff + msg_chunks[0]
                buff = ''

            msg_chunks = [x for x in msg_chunks if x]

            if not msg_chunks[-1].endswith('\r'):
                buff = msg_chunks.pop()

            for msg in msg_chunks:
                self.process_message(msg.strip('\r'))

    def process_message(self, message):
        logger.debug('<< %s' % message)

    def send(self, message):
        logger.debug('>> %s' % message)
        self.socket.send(message + ' \n')

def run(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--server', default='localhost',
                        help='The server to connect to.')
    parser.add_argument('-p', '--port', default=6667,
                        help='The port to connect to.')
    parser.add_argument('-n', '--nick', default='pybot',
                        help='The bot\'s nick.')
    parser.add_argument('-a', '--nickserv', default='nickserv',
                        help='The name of nickserv.')
    parser.add_argument('-w', '--password', default='',
                        help='The bot\'s nickserv password.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        default=False,
                        help='Turn on verbose logging.')
    parser.add_argument('channels', nargs='*', default=[])

    args = parser.parse_args(args)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    for arg, value in sorted(vars(args).items()):
        logger.info('%s = %r' % (arg, value))

    pybot = Pybot(args.server, args.port, args.nick, args.nickserv,
                  args.password, args.channels)
    pybot.connect()
