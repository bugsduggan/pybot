import sys
import time

from pybot import PybotPlugin, command


class Builtin(PybotPlugin):

    @command
    def quit(self, message='I\'m outta here'):
        """
        Makes the bot quit IRC completely.
        %(command)s [<message>]
        """
        self.bot.send('QUIT :%s' % message)
        time.sleep(1)
        sys.exit(1)

    @command
    def join(self, message):
        """
        Makes the bot join a specified channel.
        %(command)s <channel>
        """
        self.bot.send('JOIN %s' % message)

    @command
    def part(self, message, channel):
        """
        Parts from a channel. Will part the current channel if no channel
        is specified.
        %(command)s [<channel>]
        """
        if message is not None:
            self.bot.send('PART %s' % message)
        else:
            self.bot.send('PART %s' % channel)

    @command
    def help(self, message, channel, user):
        """
        Provides general help and help for specific commands.
        %(command)s [<command>]
        """
        if message is None:
            # general help
            help_string = 'Use %shelp <command> for help with a specific ' \
                'command.\n%scommands will list all available commands.' % \
                (self.bot.command_char, self.bot.command_char)
        else:
            command = self.bot.get_command(message)
            if command is None:
                help_string = 'No command called %s' % message
            else:
                help_string = command.get_help()

        self.bot.send_privmsg(channel, '%s' % help_string, target=user)

    @command
    def commands(self, channel, user):
        """
        Shows all available commands.
        %(command)s
        """
        command_string = ' '.join(
            [cmd.name for cmd in self.bot.builtin.commands])
        self.bot.send_privmsg(channel, 'builtin - %s' %
                              command_string, target=user)
        for plugin_name, plugin in self.bot.plugins.iteritems():
            command_string = ' '.join([cmd.name for cmd in plugin.commands])
            self.bot.send_privmsg(channel, '%s - %s' %
                                  (plugin_name, command_string), target=user)

    @command
    def plugins(self, channel, user):
        """
        Shows all loaded plugins.
        %(command)s
        """
        plugins = self.bot.plugins
        if len(plugins) <= 0:
            self.bot.send_privmsg(channel, 'no plugins loaded', target=user)
            return
        plugin_string = ' '.join(plugins.keys())
        self.bot.send_privmsg(channel, '%s' %
                              plugin_string, target=user)

    @command
    def reload(self, message):
        """
        Not implemented.
        """
        pass

    @command
    def unload(self, message):
        """
        Not implemented.
        """
        pass

    @command
    def load(self, message):
        """
        Not implemented.
        """
        pass
