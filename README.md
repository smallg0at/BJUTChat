# BJUTChat

## Building Client

This app can be bundled with PyInstaller. It is advised to create a new env to build this, otherwise the installer will be unnecessarily huge. 

Note: server options (`config.json`) should be tweaked before building.

An example using conda's env feature:

```bash
conda create -n univchat_build python=3.12
conda activate univchat_build
pip install -r ./requirements.txt
pyinstaller run_client.spec
```

## 