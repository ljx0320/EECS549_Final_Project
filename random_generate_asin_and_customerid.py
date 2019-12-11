import json
import random

data = {}
with open('/Users/lijiaxin/cs/EECS549/Project/insta549/data/filtered_meta_data.json') as json_file:
    data = json.loads(json_file.read())
asins = []
customerids = []
with open('/Users/lijiaxin/cs/EECS549/Project/insta549/data/test_processed_meta_data.json') as json_file:
    data = json.loads(json_file.read())
for datum in data:
    customerids.append(datum['reviewerID'])


with open('data/final_asins.txt') as f:
    asins = f.readlines()

asins = [x.strip() for x in asins]

print("Generating a random customerid from database...")
print("localhost:8000/recommend/user/" + random.choice(customerids))
print("Generating a random asin from database...")
print("localhost:8000/recommend/game/" + random.choice(asins))

