import re

from pybot import PybotPlugin, admin_command, command, trigger
from pybot.constants import CONTEXT_QUERY

# This is intended as a reference/example of all the plugin
# syntax. Not everything here has been implemented yet!


class Example(PybotPlugin):

    @command
    def foobar(self, channel):
        """
        Send the string 'foobar' to the channel the
        command was invoked from.
        """
        self.bot.send_privmsg(channel, 'foobar')

    @command
    def footarget(self, user, channel):
        """
        As above but ping the user who invoked the
        command.
        """
        self.bot.send_privmsg(channel, '%s: foobar' % user)

    @command(context=CONTEXT_QUERY)
    def fooqueue(self, user):
        """
        This can only be called from a query session.
        """
        self.bot.send_privmsg(user, 'I\'m a sausage')

    @admin_command
    def shibe(self, channel):
        """
        This can only be done by admins
        """
        self.bot.send_privmsg(channel, 'very wow, such admin')

    @trigger(re.compile(r'butts'))
    def respond_butts(self, match, channel):
        """
        This will be called anytime someone says something that matches
        that regex. A match object is also passed.
        """
        self.bot.send_privmsg(channel, 'yeah!')

    @trigger(re.compile(r'butts'), ignorecase=False)
    def butts_no_case(self, match, channel):
        """
        Same as above but the regex will be matched case
        sensitively.
        """
        self.bot.send_privmsg(channel, 'woot!')
