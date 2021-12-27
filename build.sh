#!/usr/bin/env bash

# build reactJS frontend
cd ui
npm i
npm run build

# copy frontend artefact to backend to be statically
cd ..
rm -rf server/build
cp -R ui/build server/

# build virtual environment for python backend
cd server
python -m venv venv_linux
source venv_linux/bin/activate
pip install -r requirements.txt
deactivate
