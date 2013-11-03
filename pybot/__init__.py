#! /usr/bin/env python

import argparse
from functools import wraps
import importlib
import inspect
import logging
import os
import re
import socket

from pybot.constants import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

DIR = os.path.abspath(os.path.dirname(__file__))
MAX_MESSAGE_LEN = 510


class PluginNotFoundException(Exception):
    pass


class UnboundCommandExecutionException(Exception):
    pass


def split_message(message):
    lines = list()
    for line in message.split('\n'):
        while len(line) > MAX_MESSAGE_LEN:
            start = line[:MAX_MESSAGE_LEN]
            if start != '':
                lines.append(start)
            line = line[MAX_MESSAGE_LEN:]
        if line != '':
            lines.append(line)
    return lines


class command(object):

    def __init__(self, func, context=CONTEXT_ALL):
        self.func = func
        self.name = self.func.func_name
        self.context = context
        self.plugin = None

    def __call__(self, **kwargs):
        if not self.plugin:
            raise UnboundCommandExecutionException

        func_args = dict()
        arg_names, _, _, arg_defaults = inspect.getargspec(self.func)
        arg_names.remove('self')

        if arg_defaults is None:
            arg_defaults = [None for n in arg_names]
        else:
            arg_defaults = list(arg_defaults)
            while len(arg_defaults) < len(arg_names):
                arg_defaults = [None] + arg_defaults

        for name, default in zip(arg_names, arg_defaults):
            func_args[name] = kwargs.get(name, default)

        self.plugin.logger.info('executing %s with args %r' % (
            self.func.func_name, func_args))
        self.func(self.plugin, **func_args)

    def get_help(self):
        if not self.plugin:
            raise UnboundCommandExecutionException

        docstring = self.func.__doc__
        if docstring is None or docstring == '':
            return 'No help available for command "%s"' % self.name
        else:
            command_char = self.plugin.bot.command_char
            lines = docstring.split('\n')
            lines = [l.strip() for l in lines]
            docstring = '\n'.join(lines)
            return docstring % {'command': command_char + self.name}

    def __repr__(self):
        if self.plugin:
            return '<%s command %s>' % (self.plugin, self.func.func_name)
        else:
            return '<unbound command %s>' % self.func.func_name

    def _set_plugin(self, plugin):
        self.plugin = plugin

    def match(self, context):
        if self.context is CONTEXT_ALL or self.context == context:
            return True
        return False


class PybotPlugin(object):

    def __init__(self, name, logger):
        self.name = name
        self.logger = logger
        self.command_list = list()
        self.bot = None
        self.logger.info('%s plugin loaded' % self.name)

    def __iter__(self):
        for command in self.command_list:
            yield command

    def __repr__(self):
        return '<%s plugin>' % self.name

    def _add_command(self, command):
        self.command_list.append(command)
        self.logger.info('registered %r' % command)

    def _set_bot(self, bot):
        self.bot = bot


class Pybot(object):

    def __init__(self, server, port, nick, nickserv, password, channels,
                 command_char):
        self.server = server
        self.port = int(port)
        self.nick = nick
        self.nickserv = nickserv
        self.password = password
        self.channels = channels
        self.command_char = command_char
        self.builtin = None
        self.plugins = dict()

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

        self.load_plugin('builtin')
        self.builtin = self.plugins.pop('builtin')

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

            try:
                if not msg_chunks[-1].endswith('\r'):
                    # incomplete message, defer processing
                    buff = msg_chunks.pop()
            except IndexError:
                pass  # probably quitting anyway

            for msg in msg_chunks:
                self.process_message(msg.strip('\r'))

    def load_plugin(self, plugin_name):
        path = os.path.join(DIR, 'plugins', plugin_name + '.py')

        if not os.path.isfile(path):
            raise PluginNotFoundException

        plugin_module = importlib.import_module(
            'pybot.plugins.' + plugin_name)
        plugin_class = getattr(plugin_module, plugin_name.capitalize())
        plugin_logger = logger.getChild(plugin_name)
        plugin_instance = plugin_class(plugin_name, plugin_logger)

        for cmd_name, cmd_obj in inspect.getmembers(
                plugin_instance, lambda func: isinstance(func, command)):
            cmd_obj._set_plugin(plugin_instance)
            plugin_instance._add_command(cmd_obj)

        plugin_instance._set_bot(self)
        self.plugins[plugin_name] = plugin_instance

    def process_message(self, message):
        logger.debug('<< %s' % message)

        if message.startswith('PING'):
            self.send('PONG ' + message.split()[1])

        if message.split()[1] == 'PRIVMSG':
            self.process_privmsg(message)

    def process_privmsg(self, message):
        matcher = re.search(r'^:.*!(.*)@(.*) PRIVMSG (.*) :(.*)$', message)

        kwargs = {
            'user': matcher.group(1),
            'host': matcher.group(2),
            'channel': matcher.group(3),
        }
        content = matcher.group(4)
        context = CONTEXT_CHANNEL

        if kwargs['channel'] == self.nick:
            context = CONTEXT_QUERY

        cmd = content.split()[0]
        if len(content.split()) > 1:
            kwargs['message'] = ' '.join(content.split()[1:])

        if not cmd.startswith(self.command_char):
            return
        else:
            cmd = cmd[1:]

        command = self.get_command(cmd)
        if command is not None and command.match(context):
            command(**kwargs)

    def get_command(self, cmd_name):
        for command in self.builtin:
            if command.name == cmd_name:
                return command
        for plugin in self.plugins.values():
            for command in plugin:
                if command.name == cmd_name:
                    return command
        return None

    def send(self, message):
        logger.debug('>> %s' % message)
        self.socket.send(message + '\n')

    def send_privmsg(self, channel, message, target=None):
        for line in split_message(message):
            if target is not None:
                self.send('PRIVMSG %s :%s: %s' % (channel, target, line))
            else:
                self.send('PRIVMSG %s :%s' % (channel, line))


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

    # TODO fix command char
    pybot = Pybot(args.server, args.port, args.nick, args.nickserv,
                  args.password, args.channels, '@')
    pybot.connect()
