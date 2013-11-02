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
        commands = self.bot.get_commands()
        command_string = ' '.join([cmd.name for cmd in commands])
        self.bot.send_privmsg(channel, '%s: %s' %
                              (user, command_string))

    @command
    def plugins(self, channel, user):
        plugins = self.bot.get_plugins()
        plugin_string = ' '.join([plugin.name for plugin in plugins])
        self.bot.send_privmsg(channel, '%s: %s' %
                              (user, plugin_string))

    @command
    def reload(self, message):
        pass

    @command
    def unload(self, message):
        pass

    @command
    def load(self, message):
        pass
