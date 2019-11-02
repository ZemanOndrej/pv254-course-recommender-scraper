import json
import os

path = './courses/urls/'

files = []
urls = set()
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    files = f
for js in f:
    with open(path+js, 'r') as fi:
        for url in json.load(fi):
            urls.add(url)

print(len(urls))

with open(path+'all_urls.json', 'w+', encoding="utf-8") as f:
    json.dump(list(urls), f)
