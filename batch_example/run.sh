#!/bin/bash
cd /Users/itm-mac-mini/Desktop/time_space_diagram/JSON
/usr/local/Cellar/python3/3.6.4_2/bin/python3 download_json.py

cd /Users/itm-mac-mini/Desktop/time_space_diagram
/usr/local/Cellar/python3/3.6.4_2/bin/python3 batch.py /Users/itm-mac-mini/Desktop/time_space_diagram/JSON /Library/WebServer/Documents/tradiagram/diagram/