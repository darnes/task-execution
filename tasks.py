"""
Entry point, suppose to start the process.
"""

from more_itertools import chunked
from invoke import task
from invoke.context import  Context

from remote import add

@task
def cmd(_:Context):
    """
    Just sample cmd
    """
    remote_task = add.s(2, 3).apply_async()
    result = remote_task.wait(timeout=None, interval=0.5)
    print('the result is', result)


def generator():
    return range(103)

@task
def batch(_:Context, size=10):
    """
    Batch task execution.
    not elegant but it works.
    Might benefit from celery-batches use here.
    """
    for chunk in chunked(generator(), size):
        current_jobs = []
        print('starting chunk')
        for x in chunk:
            current_jobs.append(add.s(x, x + 1).apply_async())
        # now getting the results:
        while len(current_jobs) > 0:
            task_ref = current_jobs.pop()
            res =  task_ref.get(interval=0.1)
            # res = task_ref.wait(timeout=None, interval=0.1)
            print('got result ', res)
