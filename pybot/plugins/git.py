from pybot import PybotPlugin, command, admin_command


class Git(PybotPlugin):

    @command
    def issue(self, message, channel, user):
        """
        %(command)s <issue>
        Opens a new issue on the GitHub issue tracker.
        """
        raise NotImplementedError

    @admin_command
    def gitpull(self, channel, user):
        """
        %(command)s
        Pulls source from the develop branch of the GitHub repo and
        reloads the bot.
        """
        raise NotImplementedError
