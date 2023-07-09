import read_JSON_URL as getJson
import json
import os
import shutil
import string

data = getJson.read()

# print(data)

with open(r'C:\xampp\htdocs\data\realtime_trains.json', 'w') as outfile:
    json.dump(data, outfile)

# def del_files(dir,topdown=True):
#     for root, dirs, files in os.walk(dir, topdown):
#         for name in files:
#             pathname = os.path.splitext(os.path.join(root, name))
#             if (pathname[1] == ".json"):
#                 # .remove(os.path.join(root, name))
#                 print(pathname[0])
#                 shutil.copy(pathname[0]+ pathname[1], 'D:')

# dir = os.getcwd() 
# print(dir)
# del_files(dir) 
