# This script is for doing stats
# The first task is to check how many unique reviewers are there
import json

with open('data/filtered_meta_data.json') as json_file:
    data = json.loads(json_file.read())

s = set()
new_data = list()
for datum in data:
    if datum['asin'] not in s:
        s.add(datum['asin'])
        new_data.append(datum)
print(len(data))
print(len(new_data))
with open('data/filtered_meta_data.json', 'w') as json_file:
    json.dump(new_data, json_file)






