#!/bin/bash

python3 -m venv venv --without-pip
source venv/bin/activate
cd venv
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

cd ..
pip install -r requirements.txt
deactivate