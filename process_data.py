import json
data = []
processed_data = []
with open('data/meta_Video_Games.json') as json_file:
    data = json.loads("[" +
        json_file.read().replace("}\n{", "},\n{") +
    "]")

asin_num = 0
title_num = 0

for datum in data:
    if 'asin' in datum:
        asin_num += 1
    if 'title' in datum:
        title_num += 1
        processed_data.append({'asin': datum['asin'], 'title': datum['title']})

print(len(processed_data))
print(asin_num)
print(title_num)

with open('data/processed_meta_data.json', 'w') as f:
    json.dump(processed_data, f)

