"""
definition of commands need to be run in parallel.
"""

from celery import Celery

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

@app.task
def add(x, y):
    """
    simple task to add
    """
    print('here we are')
    return x + y
