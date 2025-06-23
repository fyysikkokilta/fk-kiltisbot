# FK kiltisbot

Kiltisbot is a bot that provides many telegram integrations to Guild of Physics' services. Its features e.g. printing Guild's calendar events to telegram user, notifying in group chats about new posts in Fiirumi and digital stoke system for Guild's candy closet. Try it: https://t.me/@Fk_kiltisbot

## Installation & running

Using kiltisbot requires `python3` and the [Poetry](https://python-poetry.org/) package manager.

Activate virtual environment with

```console
poetry install
poetry shell
```

Configure the bot by copying `bot.env.example` to `bot.env` and filling in the missing parts. For the production configuration reach out to the Guilds tech team.

After configuring the bot, you can run it with

```console
mkdir data/  # Create directory for SQLite DB
poe run
```

### Running in Docker

#### Development

Run & detach. Copy Google credentials to `google_service_account_creds.json` and set up `bot.env` in project root. Docker will create or mount a `data/` directory for the SQLite DB and create `kiltis.db` file there.

```sh
docker-compose up --build -d
```

#### Production

For production deployment, use the production docker-compose file that uses the pre-built image from GitHub Container Registry:

```sh
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration

Bot is configured with environment variables. File `bot.env.example` contains all variables that are needed to enjoy full functionality of kiltisbot. Copy file and name it `bot.env` and fill missing parts.

For the production configuration reach out to the Guilds tech team.

## Calendar events & Drive backup

The calendar functionality and Drive backups use a Google service account. This can be created in the [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts). The service account needs to have the following permissions:

- Google Calendar API (read-only)
- Google Drive API (read-write)

The sheets used for backup need to be shared with the service account email (ACCOUNTNAME@PROJECTNAME.iam.gserviceaccount.com) with edit permissions for the backup to work.

## Fiirumi

Press `/subscribe` in chat where you want to have notifications about new posts after you have added bot to chat.

The subscribed chats are persisted in `data/fiirumi_data.json`. If you want to unsubscribe Fiirumi notifications from some chat, you can remove the chat from the file.

## Drive backend

Drive backend uses same token as calendar module. Drive backend enables importing and exporting database with telegram commands that are only available for admin users.

## Bugs and issues

Many. Some of them are documented in the source code as TODO comments. You can find them by typing

```console
grep -r TODO $(ls -I env)
```

in the roof folder. Opening new issues in Github and sending pull requests is welcomed.
