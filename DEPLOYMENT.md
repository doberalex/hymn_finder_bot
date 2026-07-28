# Deployment Notes

Project path:

`/Users/aleksandr/Documents/PROJECTS/DOBER/doberalex/public_html/hymn_finder_bot`

GitHub repository:

`https://github.com/doberalex/hymn_finder_bot`

PhpStorm deployment target:

- Server name: `MY SERVER TW`
- Access type: `SFTP`
- Host: `92.53.96.117`
- Port: `22`
- User: `doberalex`
- Remote root: `/home/d/doberalex`
- Mapping: local `public_html` to remote `/public_html`
- Local project: `/Users/aleksandr/Documents/PROJECTS/DOBER/doberalex/public_html/hymn_finder_bot`
- Remote project: `/home/d/doberalex/public_html/hymn_finder_bot`

## Secrets

Runtime credentials are stored in `.env`. The real `.env` is excluded from Git;
only `.env.example` is committed. Required keys:

- `BOT_TOKEN`
- `ADMIN_ID`
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

## Deployment from Codex

1. Open the project or required file in PhpStorm.
2. Select the `hymn_finder_bot` folder in Project View.
3. Use `Tools > Deployment > Upload to MY SERVER TW`.
4. For a small update, upload only the changed files.

This is the same deployment profile and method as the neighboring
`scheduling` project. The only difference is the folder:
`public_html/hymn_finder_bot`.

Notes:

- Do not upload unrelated folders from `public_html`.
- `.env` is deployed over SFTP but is never committed to Git.
- `venv`, `.git`, logs and cache files are excluded from Git and should not be
  uploaded as application source.
