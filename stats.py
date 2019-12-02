# This script is for doing stats
# The first task is to check how many unique reviewers are there
import json

with open('data/processed_Video_Games.json') as json_file:
    data = json.loads(json_file.read())

"""
s = set()
for datum in data:
    if datum["reviewerID"] not in s:
        s.add(datum["reviewerID"])
print(len(s))
"""




