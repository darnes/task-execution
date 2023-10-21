# About 
Snipped to quickly get started with multiple parallel tasks execution. 


# Dependencies:
 * python 3+
 * docker


```bash
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
# Quick start
1. run redis:
```bash
docker run -p 6379:6379 redis
```
2. Run celery worker (as many as you need)
```bash
celery -A remote worker --loglevel=INFO
```

3. Start basic command
```bash
invoke cmd
```

4. Enjoy.
   
