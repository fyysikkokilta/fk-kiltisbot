## Installation
Running kiltisbot requires `python3` and `virtualenv` package. You can install `virtualenv` with
```console
python3 -m pip install --user virtualenv
```
or you can install it globally without `--user` flag. Create virtual environment for bot with
```console
python3 -m venv env
```
and activate environment and install dependencies with
```console
source env/bin/activate
pip install -r requirements.txt
```
To start bot in test or production mode run
```console
python3 kiltisbot.py      # production
python3 kiltisbot.py TEST # test
```
`Ctrl+C` stops the bot. You might want to start bot in `tmux` session. To do so run
```console
tmux new -s kiltisbot
```
Inside session start bot as above and detach from session by pressing `Ctrl+b+d`. You can later return to the session with
```console
tmux a -t kiltisbot
```

TODO document all the other stuff
