"""
useless - stays here just to keep contents of story.md consistent
"""
from invoke.context import Context
from fabric import task

from fabric.group import Group

g = Group(['h1', 'h2'])

@task
def cmd(c: Context):
    """
    basic command
    """
    print(c.host, c.port) # , c.anything_you_might_think_of
    print('here we are')
