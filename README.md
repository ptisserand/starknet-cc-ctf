# Python environment setup

## Create virtual environment
```
$ python -m venv .venv
$ source .venv/bin/activate
```
## Install dependencies
```
$ pip intall -r requirements.txt
```

# Execute challenge hack
Just run `./challenge.bash CHALLENGE_NAME`, e.g:
```
$ ./challenge.bash access-denied
```
This shell script will stop already running challenge container, build challenge container, start it and then run the challenge python `hack.py` script

