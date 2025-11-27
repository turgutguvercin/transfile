## Update site languages (Django i18n)

This project already has i18n configured via `LocaleMiddleware`, `LOCALE_PATHS`, and `LANGUAGES` in `translate/translator/settings.py`. Use these steps to update translations or add a new language.

### 1) Prerequisites
- Activate the virtualenv: `./venv/Scripts/activate` (Windows PowerShell)
- Run commands from the project root (the folder containing `manage.py`).
- Install GNU gettext tools (required by compilemessages):
  - Download the gettext from here https://mlocati.github.io/articles/gettext-iconv-windows.html ❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗❗


### 2) Where translation files live
- Source `.po` files: `locale/<lang>/LC_MESSAGES/django.po`
- Compiled `.mo` files: `locale/<lang>/LC_MESSAGES/django.mo`
- Project languages are defined in `LANGUAGES` and `PARLER_LANGUAGES` in `translate/translator/settings.py`.



### 3) Mark strings for translation
- Python: wrap user-facing text with `gettext`/`gettext_lazy` (aliases `_()` / `gettext_lazy()`)
- Templates: use `{% load i18n %}` and `{% trans %}` / `{% blocktrans %}`

### 4) Extract messages (makemessages)
Run for each language you support, ignoring generated/irrelevant directories.

PowerShell (Windows):
```powershell
python manage.py makemessages -l en --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l de --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l fr --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l es --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l it --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l ru --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l ja --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l zh-hans --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
python manage.py makemessages -l tr --ignore=venv --ignore=node_modules --ignore=migrations --ignore=__pycache__ --ignore=*.txt --ignore=*.md
```

### 5) Translate `.po` files
Edit each `locale/<lang>/LC_MESSAGES/django.po` and fill in `msgstr` entries.
- Keep placeholders (e.g., `%(name)s`, `{count}`) intact
- Preserve HTML and punctuation

### 6) Compile translations
```bash
python manage.py compilemessages
```
This generates/updates `.mo` files.

### 7) Verify in the app
- Restart the server if running
- Use language switch mechanisms (URL, session, or subdomain) and verify pages

### 8) Adding a new language
1. Add the language to `LANGUAGES` in `translate/translator/settings.py`
2. Add the language to `PARLER_LANGUAGES` if you need model translations
3. Run makemessages for the new language
4. Translate the new `django.po`
5. Run compilemessages

### Troubleshooting
- "msgfmt not found": install gettext and ensure it is on PATH, or run from Git Bash
- Changed strings not appearing: re-run makemessages, then re-compile, clear `.mo` if needed
- Mixed `zh_Hans` vs `zh-hans`: standardize on `zh-hans` to match settings; rename directory and recompile


