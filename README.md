# BJUTChat

## Building Client

This app can be bundled with PyInstaller. It is advised to create a new env to build this, otherwise the installer will be unnecessarily huge. 

Note: server options (`config.json`) should be tweaked before building.

### Dependencies outside Python packages

- tkinter

### Examples

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
## Running File Server

With python3 native venv, on bash:

```bash
python3 -m venv bjutchat_env
source bjutchat_env/bin/activate
pip install -r ./requirements.txt
pip install -r ./requirements_extra.txt
python3 ./file_server/init_db.py # Initializes & cleans database
python3 ./run_file_server.py
```
## Running Chat Server

With python3 native venv, on bash:

```bash
python3 -m venv bjutchat_env
source bjutchat_env/bin/activate
pip install -r ./requirements.txt
pip install -r ./requirements_extra.txt
python3 ./server/excute_sql.py # Initializes & cleans database
python3 ./run_server.py
```

## Running dashboard

Must perform after starting chat server. Not safe, dont use unless required.

```bash
python3 ./run_dashboard.py
```