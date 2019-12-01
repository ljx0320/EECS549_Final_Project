# This script is for doing stats
# The first task is to check how many unique reviewers are there
import json

with open('data/processed_Video_Games.json') as json_file:
    data = json.loads("[" +
        json_file.read().replace("}\n{", "},\n{") +
    "]")