#!/bin/bash
pkill -f -INT backendcoms.py
pkill -f -INT backendcoms.py
pkill -f -INT backendcoms.py
pkill -f -INT reactorlocal.py
pkill -f -INT reactorlocal.py

source /home/hacklab/.virtualenvs/reactorconsole/bin/activate
cd ~/devel/odysseus-python/reactorconsole
#./backendcoms.py --id jump_reactor --url http://192.168.1.2 &
./backendcoms.py --id jump_reactor --url https://apps.odysseuslarp.dev --user odysseus --passwd 2024 --verbose
./reactorlocal.py
pkill -f -INT backendcoms.py
pkill -f -INT backendcoms.py
pkill -f -INT backendcoms.py
