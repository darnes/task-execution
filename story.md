In the course of my career I I  notice finding myself multiple times in the point where I need some tool to automate my actions.
In many cases the problem were solved by `yarn run` or make file.
But every time this task was involving the remote command execution I hit the wall.
Surprisingly this wall looks very similar every time I see it.
In old times `good old fabric` and  `fabfile` can do the job. But now days with new fabric I have no idea  how I  can  adjust it to my needs. Alternatives includes `ansible`, `chef`.
Chef is perfect except it's not.  It requires agent. My experience tells me that the last thing one want to do to be able to run the command is go and run one more command manually. Especially if task  involves provisioning of the newly installed OS.

ANsible is nice but it is way to huge. Also concept of describing state in yaml doesn't do very well. Wherever you do - you most likely will end up writing python plugin for ansible to do exactly what you need.
But hold on, how about get to the end and start with python code that do just that simple thing you need to be done.

So this article I'll follow the steps to setup `sort of old good fabric` in order to run simple job across the fleet  aka 100+ servers. The inventory(collection of servers) should be dynamic and iterator-based, the credentials should be dynamic, the library of commands should be easy to keep clean and clear.
I reckon it can be nice tool to  easily  automate  my daily tasks as well as improve my general performance.

So let's get started.
1. Exploration.

Task runner.
hm turns out old good fabric is still here:
https://flask.palletsprojects.com/en/1.1.x/patterns/fabric/#:~:text=Fabric%20is%20a%20tool%20for,Flask%20applications%20to%20external%20servers.

let's try it out.

env:
```bash
❯ virtualenv .venv
❯ source .venv/bin/activate
❯ python --version
Python 3.9.17

❯ pip install fabric
❯ pip freeze | grep fabric
fabric==3.2.2
# nice... so let's see what it can do. 

```
https://www.fabfile.org/
ok, docs somewhat terrible there is no easy to get started guide... 
I'd like to copy - paste and run and then start thinking of what am I doing... 


hm, the warning here:
 https://www.fabfile.org/installing.html
 says about fabric3 they don't control.... hm... 
 https://pypi.org/project/Fabric3/
 https://github.com/mathiasertl/fabric/
 ```python
from invoke.context import Context
from fabric import task

@task
def cmd(c: Context):
    print('here we are')
```

```bash
❯ fab cmd
here we are
```

so it kind of works. 
multiple hosts:
```bash
❯ fab -H t1,t2 cmd
here we are
here we are
```

getting access to the host name. 

ok, looking at the context object:
```python
    def __init__(self, config: Optional[Config] = None) -> None:
        ....
        config = config if config is not None else Config()
        self._set(_config=config)
...
    def _set(self, *args: Any, **kwargs: Any) -> None:
        ...
        if args:
            object.__setattr__(self, *args)
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
```

as good as any dict based on the config ... nice. 

```python
from invoke.context import Context
from fabric import task

@task
def cmd(c: Context):
    """
    docstring
    """
    print(c.host, c.port) 
```

doe to the way context is implemented following doesn't give any compilation error:
```python
from invoke.context import Context
from fabric import task

@task
def cmd(c: Context):
    """
    docstring
    """
    print(c.host, c.port, c.anything_you_might_think_of) 
```

what if gives instead is the error during the runtime:

```python
AttributeError: No attribute or config key found for 'anything_you_might_think_of'
```

nice.... 
So effectively what we can rely on is the debugger or `print(dir(c))`.

Great that we have a typing now. Will be nice to start using it as well. 

ok, we have what we have.

So far for my purpose that should be enough. 


Let's see how we can use inventory.
My goal here is to make inventory dynamic to the extend it should work as generator. 

ok The Group looks like what I do need here:
https://docs.fabfile.org/en/latest/api/group.html

except there is no even single example of usage.... 
ok. 

let's try to make one. 

found collection object in the fab cli help.
Fabric [docs](https://docs.fabfile.org/en/latest/cli.html) says:
```By default, fab honors all of the same CLI options as Invoke’s ‘inv’ program; only additions and overrides are listed here!```
inv documentation here we go:
https://docs.pyinvoke.org/en/latest/invoke.html#inv

hm, at this point I'm not very interested in ssh communication features of fabric. 
WHat if invoke is exactly what I'm looking for. 
let's try it. 

ok, it is the same context ... 

Let's see how we can extend input... 
AS in this case the inventory is just a collection... 

Finally found what has happened to original fabric: https://www.pyinvoke.org/faq.html
now my thoughts are clearer. 
alternatives outlined nicely:
https://www.pyinvoke.org/prior-art.html

well, sound like I'm on the right spot. 
now, chaining the tasks. Effectively what I need is to run single command against big input in bulks. 

ok, trying to use iterator to populate the input:
```python
from invoke import task
from invoke.context import  Context

def hosts_iter():
    for t in range(10):
        yield t

@task
def get_hosts(c: Context):
    """
    """
    c.hosts = hosts_iter()


@task(get_hosts)
def cmd(c: Context):
    """
    Just sample cmd
    """
    print('here we are', c.hosts, list(c.hosts))
```

getting:
```python
  File "/Users/dimas/proj/articles/fabric/.venv/lib/python3.9/site-packages/invoke/config.py", line 1223, in merge_dicts
    base[key] = copy.copy(value)
  File "/usr/local/Cellar/python@3.9/3.9.17_1/Frameworks/Python.framework/Versions/3.9/lib/python3.9/copy.py", line 92, in copy
    rv = reductor(4)
TypeError: cannot pickle 'generator' object
```

well it only means that I can't pass the python objects across  the tasks.... 
heh. ok, need to manually run task in bulks then. 

hm, why I have a strange feeling that I'm re-inventing celery here. 
```bash
pip  install celery
```

for that I need a broker.... 
RabbitMQ it is. 
```bash
docker run -p 5672:5672 rabbitmq
```
starting worker
```bash
celery -A remote worker --loglevel=INFO
```

ok, rabbitMq can't  be result backend. 
ok making it redis.... 
```bash
pip install -U "celery[redis]"
```

```
docker run -p 6379:6379 redis
```

