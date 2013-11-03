import sys
import time

from pybot import PybotPlugin, command, PluginNotFoundException, admin_command


class Builtin(PybotPlugin):

    @admin_command
    def quit(self, message='I\'m outta here'):
        """
        %(command)s [<message>]
        Makes the bot quit IRC completely.
        """
        self.bot.send('QUIT :%s' % message)
        time.sleep(1)
        sys.exit(1)

    @admin_command
    def join(self, message):
        """
        %(command)s <channel>
        Makes the bot join a specified channel.
        """
        self.bot.send('JOIN %s' % message)

    @admin_command
    def part(self, message, channel):
        """
        %(command)s [<channel>] [<message>]
        Parts from a channel. Will part the current channel if no channel
        is specified.
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
        %(command)s [<command>]
        Provides general help and help for specific commands.
        """
        if message is None:
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
        %(command)s
        Shows all available commands.
        """
        command_string = ' '.join(
            [cmd.name for cmd in self.bot.builtin.command_list])
        self.bot.send_privmsg(channel, 'builtin - %s' %
                              command_string, target=user)
        for plugin_name, plugin in self.bot.plugins.iteritems():
            command_string = ' '.join(
                [cmd.name for cmd in plugin.command_list])
            self.bot.send_privmsg(channel, '%s - %s' %
                                  (plugin_name, command_string), target=user)

    @command
    def plugins(self, channel, user):
        """
        %(command)s
        Shows all loaded plugins.
        """
        plugins = self.bot.plugins
        if len(plugins) <= 0:
            self.bot.send_privmsg(channel, 'no plugins loaded', target=user)
            return
        plugin_string = ' '.join(plugins.keys())
        self.bot.send_privmsg(channel, '%s' %
                              plugin_string, target=user)

    @admin_command
    def reload(self, message, channel, user):
        """
        %(command)s <plugin>
        Reloads a plugin.
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

    @admin_command
    def unload(self, message, channel, user):
        """
        %(command)s <plugin>
        Unloads a plugin.
        """
        try:
            self.bot.plugins.pop(message)
            self.bot.send_privmsg(channel, '%s plugin unloaded' %
                                  message, target=user)
        except KeyError:
            self.bot.send_privmsg(channel, '%s plugin not found' %
                                  message, target=user)

    @admin_command
    def load(self, message, channel, user):
        """
        %(command)s <plugin>
        Loads a plugin.
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
        %(command)s [<channel>] <message>
        Makes the bot say something.
        """
        message = message.strip()
        if message.split()[0].startswith('#') or \
                message.split()[0].startswith('@'):
            channel = message.split()[0]
            message = ' '.join(message.split()[1:])
        self.bot.send_privmsg(channel, message)

    @command
    def admins(self, channel, user):
        """
        %(command)s
        Lists all admins.
        """
        admin_list = self.bot.admins
        self.bot.send_privmsg(channel, '%s' % admin_list, target=user)

    @admin_command
    def mkadmin(self, channel, user, message):
        """
        %(command)s <user>
        Grants a user admin privileges.
        """
        if message is None:
            self.bot.send_privmsg(channel, 'You must specify a user',
                                  target=user)
            return
        self.bot.admins.append(message)
        self.bot.send_privmsg(channel, '%s is now an admin' % message,
                              target=user)

    @admin_command
    def rmadmin(self, channel, user, message):
        """
        %(command)s <user>
        Removes admin privileges from a user.
        """
        if message is None:
            self.bot.send_privmsg(channel, 'You must specify a user',
                                  target=user)
            return
        if message == self.bot.owner:
            self.bot.send_privmsg(channel, 'You can\'t remove the '
                                  'owner\'s admin priveleges', target=user)
            return
        try:
            self.bot.admins.remove(message)
            self.bot.send_privmsg(channel, '%s is no longer an admin' %
                                  message, target=user)
        except ValueError:
            self.bot.send_privmsg(channel, '%s is not an admin' % message,
                                  target=user)
