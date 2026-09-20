# Secure Messaging System

This is a small Django project I made where people can sign up, but they don't get an account straight away — an admin has to approve them first. After that they can log in and send messages to each other, and the messages are stored encrypted (not plain text) in the database.

Made this while learning Django, so the code is pretty basic, nothing too fancy.

## What it can do

- Signup form — but it doesn't create the account right away. It just saves a "pending" request.
- After you submit the form, the page keeps checking every 2 seconds if admin approved you or not (using a bit of JavaScript + a small API endpoint). No need to refresh the page.
- Normal login/logout using Django's own auth system.
- Every user has a role — either `user` or `admin`. Admin gets extra options that normal users can't see.
- Users can see other users and send them messages.
- Messages get encrypted before saving (used AES, learned it from a tutorial, added it in `crypto.py`).
- Users have an inbox where they can see messages sent to them (auto decrypted).
- Admin has a page to see all pending signup requests and can Allow or Deny each one.
- Admin can also pick 2 users and check their conversation (shown as encrypted text first, then admin can put in a password to actually read it).
- Admin can remove any normal user's account.

## Folder structure (basically)

```
SecureMessagingSystem/
├── accounts/
│   ├── models.py     -> Profile, RegistrationRequest, Message (the tables)
│   ├── views.py       -> all the functions/logic
│   ├── urls.py        -> all the links/paths
│   ├── crypto.py      -> encrypt/decrypt stuff
│   ├── management/commands/create_default_admin.py  -> makes a default admin
│   └── templates/accounts/   -> all the html pages
├── config/
│   └── settings.py
├── manage.py
└── db.sqlite3
```

## How to run it

Easiest way — just double-click `setup.bat` in the project folder. It does everything below automatically (creates env, installs stuff, runs migrations, makes admin, starts server).

If you want to do it manually instead:

First make a virtual env and activate it:

```bash
python -m venv venv
venv\Scripts\activate
```

Then install stuff:

```bash
pip install django
pip install cryptography
```

Then set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

Make a default admin account (already coded in a command):

```bash
python manage.py create_default_admin
```

Then just run:

```bash
python manage.py runserver
```

Open your browser and go to `http://127.0.0.1:8000/`

## Admin login

I hardcoded a default admin in `create_default_admin.py`:
- Username: `Humhai`
- Password: `hojabhai333`

## How it actually works (step by step)

1. New person goes to the site, fills username/password/age, hits submit.
2. This doesn't make a real account. It just creates a `RegistrationRequest` with status `PENDING`.
3. While waiting, the page keeps asking the server (every 2 sec) "hey has admin approved this yet?"
4. Admin logs in, goes to the verify page, sees the pending list, clicks Allow or Deny.
   - If Allow → a real account gets created for that person.
   - If Deny → nothing gets created, request just gets marked denied.
5. Person can now log in with the account (if approved).
6. Any logged in user can go to "message users" and send someone a message — it gets encrypted before saving.
7. Person can check their inbox to read messages sent to them.
8. Admin also has extra pages to check any conversation or remove a user.

## Notes / things to know

- This was made for learning purposes, not a real production app.
- `DEBUG = True` is on in settings — should be turned off if this was ever going live for real.
- Passwords for signup requests are hashed before saving, so they're not stored in plain text even while pending.