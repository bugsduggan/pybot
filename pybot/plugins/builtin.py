import sys
import time

from pybot import PybotPlugin, command


class Builtin(PybotPlugin):

    @command
    def quit(self, message='I\'m outta here'):
        self.bot.send('QUIT :%s' % message)
        time.sleep(1)
        sys.exit(1)

    @command
    def join(self, message):
        self.bot.send('JOIN %s' % message)

    @command
    def part(self, message, channel):
        if message is not None:
            self.bot.send('PART %s' % message)
        else:
            self.bot.send('PART %s' % channel)

    @command
    def help(self, message):
        pass

    @command
    def commands(self, channel, user):
        commands = self.bot.commands()
        self.bot.send_privmsg(channel, '%s: %r' %
                              (user, ' '.join([cmd.name for cmd in commands])))

    @command
    def plugins(self, message):
        pass

    @command
    def reload(self, message):
        pass

    @command
    def unload(self, message):
        pass

    @command
    def load(self, message):
        pass
