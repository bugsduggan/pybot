import sys
import time

from pybot import PybotPlugin, command, PluginNotFoundException


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
        %(command)s [<channel>] [<message>]
        """
        if message is not None:
            if message.split()[0].startswith('#') or \
                    message.split()[0].startswith('@'):
                channel = message.split()[0]
                message = ' '.join(message.split()[1:])
            self.bot.send('PART %s %s' % (channel, message))
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
    def foobar(self, channel, user):
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
    def reload(self, message, channel, user):
        """
        Reloads a plugin.
        %(command)s <plugin>
        """
        try:
            self.bot.plugins.pop(message)
            self.bot.load_plugin(message)
            self.bot.send_privmsg(channel, '%s plugin reloaded' %
                                  message, target=user)
        except KeyError:
            self.bot.send_privmsg(channel, '%s plugin not found' %
                                  message, target=user)
        except PluginNotFoundException:
            self.bot.send_privmsg(channel, '%s plugin not found' %
                                  message, target=user)
        except Exception as err:
            self.bot.send_privmsg(channel, '%s: %s' %
                                  (repr(err), err.message), target=user)

    @command
    def unload(self, message, channel, user):
        """
        Unloads a plugin.
        %(command)s <plugin>
        """
        try:
            self.bot.plugins.pop(message)
            self.bot.send_privmsg(channel, '%s plugin unloaded' %
                                  message, target=user)
        except KeyError:
            self.bot.send_privmsg(channel, '%s plugin not found' %
                                  message, target=user)

    @command
    def load(self, message, channel, user):
        """
        Loads a plugin.
        %(command)s <plugin>
        """
        try:
            self.bot.load_plugin(message)
            self.bot.send_privmsg(channel, '%s plugin loaded' %
                                  message, target=user)
        except PluginNotFoundException:
            self.bot.send_privmsg(channel, '%s plugin not found' %
                                  message, target=user)
        except Exception as err:
            self.bot.send_privmsg(channel, '%s: %s' %
                                  (repr(err), err.message), target=user)

    @command
    def say(self, message, channel):
        """
        Makes the bot say something.
        %(command)s [<channel>] <message>
        """
        message = message.strip()
        if message.split()[0].startswith('#') or \
                message.split()[0].startswith('@'):
            channel = message.split()[0]
            message = ' '.join(message.split()[1:])
        self.bot.send_privmsg(channel, message)
