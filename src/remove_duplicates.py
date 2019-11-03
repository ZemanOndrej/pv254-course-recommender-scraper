import json
import os

path = './courses/urls/'

files = []
urls = set()
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    files = f

sets = {}


for js in f:
    sets[js] = set()
    with open(path+js, 'r') as fi:
        for url in json.load(fi):
            sets[js].add(url)


for key in sets:
    with open(path+key, 'w') as fi:
        json.dump(list(sets[key]), fi, indent=4)
