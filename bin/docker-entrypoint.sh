#!/bin/bash

pip install -r requirements.txt
pyb
pip install -e ./target/dist/yapo-0.1.0.dev/

jupyter notebook \
         --notebook-dir=src/main/scripts \
         --FileNotebookManager.checkpoint_dir='/tmp/.ipynb_checkpoints' \
         --ip='*' --port=8888 \
         --no-browser \
         --NotebookApp.token='' \
         --allow-root
