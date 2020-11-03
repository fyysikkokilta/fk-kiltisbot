# FK kiltisbot
Kiltisbot is a bot that provides many telegram integrations to Guild of Physics' services. Its features e.g. printing Guild's calendar events to telegram user, notifying in group chats about new posts in Fiirumi and digital stoke system for Guild's candy closet. Try it: https://t.me/@Fk_kiltisbot

## Installation
Running kiltisbot requires `python3` and `virtualenv` package. You can install `virtualenv` with
```console
python3 -m pip install --user virtualenv
```
or you can install it globally without `--user` flag or you can install it with you disributions package manager. Create virtual environment for bot with
```console
python3 -m venv env
```
and activate environment and install dependencies with
```console
source env/bin/activate
pip install -r requirements.txt
```
To start bot
```console
python3 bot.py
```
`Ctrl+C` stops the bot. You might want to start bot in `tmux` session. To do so run
```console
tmux new -s kiltisbot
```
Inside session start bot as above and detach from session by pressing `Ctrl+b+d`. You can later return to the session with
```console
tmux a -t kiltisbot
```

## Configuration
Bot is configured with python file. File `config-example.py` contains all variables that are needed to enjoy full functionality of kiltisbot. Copy file and name it `config.py` and fill missing parts.

## Calendar events
First you have to create `credentials.json` file in [Google API Console Credentials page](https://console.developers.google.com/apis/credentials). Select `create credentials` -> `OAuth cliend ID` -> select `Desktop app` for application type. Export json file, name it as `credentials.json` and place it in project root.

You need `token.pickle` file in your project root for calendar events to work correctly. When bot is started first time (when `google_auth` is imported first time) browser window opens where you can sign up with your Google account to get token.

## Fiirumi
Press `/subscribe` in chat where you want to have notifications about new posts after you have added bot to chat.

## Drive backend
Drive backend uses same token as calendar module. Drive backend enables importing and exporting database with telegram commands that are only available for admin users.

## Bugs and issues
Many. Some of them are documented in the source code as TODO comments. You can find them by typing
```console
grep -r TODO $(ls -I env)
```
in the roof folder. Opening new issues in Github and sending pull requests is welcomed.