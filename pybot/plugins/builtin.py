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
    def foobar(self, channel, user):
        command_string = ' '.join(
            [cmd.name for cmd in self.bot.builtin.commands])
        self.bot.send_privmsg(channel, '%s: builtin - %s' %
                              (user, command_string))
        for plugin_name, plugin in self.bot.plugins.iteritems():
            command_string = ' '.join([cmd.name for cmd in plugin.commands])
            self.bot.send_privmsg(channel, '%s: %s - %s' %
                                  (user, plugin_name, command_string))

    @command
    def plugins(self, channel, user):
        plugins = self.bot.plugins
        if len(plugins) <= 0:
            self.bot.send_privmsg(channel, '%s: no plugins loaded' % user)
            return
        plugin_string = ' '.join(plugins.keys())
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
