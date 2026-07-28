# Deployment Notes

Project path:

`/Users/aleksandr/Documents/PROJECTS/DOBER/doberalex/public_html/hymn_finder_bot`

GitHub repository:

`https://github.com/doberalex/hymn_finder_bot`

Server:

- Host: `92.53.96.117`
- Port: `22`
- User: `doberalex`
- Remote project: `/home/d/doberalex/public_html/hymn_finder_bot`

## Secrets

Runtime credentials are stored in `.env`. The real `.env` is excluded from Git;
only `.env.example` is committed. Required keys:

- `BOT_TOKEN`
- `ADMIN_ID`
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

## Initial deployment

```bash
cd /home/d/doberalex/public_html
git clone https://github.com/doberalex/hymn_finder_bot.git
cd hymn_finder_bot
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
# Fill .env with production credentials.
chmod 600 .env
chmod +x run_bot.sh
./run_bot.sh
```

If the hosting account cannot access a private GitHub repository, upload the
first version over SFTP or configure a GitHub deploy key before cloning.

## Updating

```bash
cd /home/d/doberalex/public_html/hymn_finder_bot
git pull --ff-only
venv/bin/pip install -r requirements.txt
pkill -f "/home/d/doberalex/public_html/hymn_finder_bot/run.py"
./run_bot.sh
```

Check status:

```bash
pgrep -af "/home/d/doberalex/public_html/hymn_finder_bot/run.py"
tail -n 100 bot.log
```

PhpStorm SFTP target (as in the neighboring `scheduling` project):

- Server name: `MY SERVER TW`
- Mapping: local project root to `/`

For normal updates, Git deployment is preferred because it keeps the server
version aligned with the repository.
