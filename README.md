# BJUTChat

A simple chat application tailiored for university uses, mainly Python-based, with Curve25519 encryption support. 

Project is no longer maintained, and you are free to clone in compliance to the license.

## Features

- Register / Login
- Manage friends (request, remove)
- Manage Groups (join, create)
- Group User Privilige (group user, admin, creator; invite / kick / set admin)
- Change Username
- Messages (receive / send raw text, image, files)
- Admin portal for management

## Structure

- `/admin_dashboard` is a admin dashboard (Python + Flask)
  - Note it have no WSGI support and could only be run with the flask dev server
- `/client` is client code. (Python + tKinter)
- `/file_server` is file server. (Python + Flask)
- `/server` is chat server. (Python)

## Requirements

- Python 3.10+
- Windows 10+, Any Linux, macOS 10.11+
- Anything stringer than a potato

## Deployment

Follow the steps below:

- Deploy file_server
- Deploy server. Before starting, set server port in `config.json`.
- Fill up the config json with client related info in `config.json` before you compile.
- Build client
- (optional) Start up admin dashboard

### Building Client

This app can be bundled with PyInstaller. It is advised to create a new env to build this, otherwise the installer will be unnecessarily huge. 

Note: server options (`config.json`) should be tweaked before building.

#### Dependencies outside Python packages

- tkinter

#### Examples

An example using conda's env feature:

```bash
conda create -n univchat_build python=3.12
conda activate univchat_build
pip install -r ./requirements.txt
pyinstaller run_client.spec
```

With python3 native venv, on bash:

```bash
python3 -m venv bjutchat_env
source bjutchat_enc/bin/activate
pip install -r ./requirements.txt
pyinstaller run_client.spec
```
### Running File Server

With python3 native venv, on bash:

```bash
python3 -m venv bjutchat_env # Watch out for dependencies!
source bjutchat_env/bin/activate
pip install -r ./requirements.txt
pip install -r ./requirements_extra.txt
python3 ./file_server/init_db.py # Initializes & cleans database
python3 ./run_file_server.py
```
### Running Chat Server

With python3 native venv, on bash:

```bash
python3 -m venv bjutchat_env
source bjutchat_env/bin/activate
pip install -r ./requirements.txt
pip install -r ./requirements_extra.txt
python3 ./server/excute_sql.py # Initializes & cleans database
python3 ./run_server.py
```

### Running dashboard

Must perform after starting chat server. Not safe, dont use unless required.

```bash
python3 ./run_dashboard.py
```