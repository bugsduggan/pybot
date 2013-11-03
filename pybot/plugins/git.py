from getpass import getpass
import os

from github3 import authorize, login

from pybot import PybotPlugin, command, admin_command

TOKEN_FILE = '.github.token'


class Git(PybotPlugin):

    def init(self):
        if not os.path.isfile(TOKEN_FILE):
            user = raw_input('GitHub username: ')
            password = ''
            while not password:
                password = getpass('Password for {0}: '.format(user))
            scopes = ['repo']
            auth = authorize(user, password, scopes)
            with open(TOKEN_FILE, 'w') as fd:
                fd.write(auth.token + '\n')
            self.logger.info('GitHub token written to %s' % TOKEN_FILE)
        self.token = ''
        with open(TOKEN_FILE, 'r') as fd:
            self.token = fd.readline().strip()

    def get_repo(self):
        gh = login(token=self.token)
        return gh.repository('bugsduggan', 'pybot')

    @command
    def issue(self, message, channel, user):
        """
        %(command)s <issue>
        Opens a new issue on the GitHub issue tracker.
        """
        repo = self.get_repo()
        body = 'Issue created by pybot\'s git plugin by %s in %s' % \
            (user, channel)
        issue = repo.create_issue(title=message, body=body)
        self.bot.send_privmsg(channel, 'Issue #%d created: %s' %
                              (issue.number, issue.html_url), target=user)

    @admin_command
    def gitpull(self, channel, user):
        """
        %(command)s
        Pulls source from the develop branch of the GitHub repo and
        reloads the bot.
        """
        raise NotImplementedError
