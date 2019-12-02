import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import json

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_colwidth', -1)

# read meta data
metadata_df = pd.read_json('data/filtered_meta_data.json')
print(metadata_df.head(10))
metadata_df.asin = metadata_df.asin.astype(object)
print(metadata_df.dtypes)
# read rating data
rating_df = pd.read_json('data/processed_Video_Games.json')
print(rating_df.head(10))
print(rating_df.dtypes)
# merge two data sets on asin
merged_df = pd.merge(metadata_df, rating_df, on='asin')
print(merged_df.head(10))
print(merged_df.iloc[45587])
print(merged_df.shape)
# print(merged_df.describe())

# get the mean rating for every video game
ratings_df = pd.DataFrame(merged_df.groupby('asin')['rating'].mean())
users_df = pd.DataFrame(merged_df.groupby('reviewerID')['rating'].mean())
print(merged_df.head())
# but we also need to consider the number of ratings for each video game
ratings_df['number_of_ratings'] = merged_df.groupby('asin')['rating'].count()
users_df['number_of_ratings'] = merged_df.groupby('reviewerID')['rating'].count()
print("users_df heads")


sorted_users = users_df.sort_values('number_of_ratings', ascending=False)
i = 0
users = set()
games = set()
for i in range(sorted_users.shape[0]):
    if sorted_users.iloc[i]["number_of_ratings"] <= 5.0:
        break
    users.add(str(sorted_users.iloc[i].name))
print(len(users))

print(ratings_df.sort_values('number_of_ratings', ascending=True).iloc[20000])

number_of_ratings = ratings_df.sort_values('number_of_ratings', ascending=False)
i = 0
for i in range(number_of_ratings.shape[0]):
    if number_of_ratings.iloc[i]["number_of_ratings"] <= 5.0:
        break
    games.add(str(number_of_ratings.iloc[i].name))
print(len(games))

with open('data/processed_Video_Games.json') as json_file:
    data = json.loads(json_file.read())
processed_Video_Games = []
for datum in data:
    if datum["asin"] in games and datum["reviewerID"] in users:
        processed_Video_Games.append(datum)
with open('data/test_processed_meta_data.json', 'w') as f:
    json.dump(processed_Video_Games, f)



print(ratings_df.sort_values('number_of_ratings', ascending=True).shape)
print(ratings_df.head(12))
ratings_df['rating'].hist(bins=50)
plt.show()
ratings_df['number_of_ratings'].hist(bins=60)
plt.show()

users_df['number_of_ratings'].hist(bins=60)
plt.show()

sns.jointplot(x='rating', y='number_of_ratings', data=ratings_df)
plt.show()
print(merged_df.iloc[0])

test_merged_df = merged_df.iloc[1:1000]
user_games_df = test_merged_df.pivot_table(index='reviewerID', columns='asin', values='rating')
print(user_games_df.head())
# now create a matrix including all users (row) and all games (column)
# user_games_df = merged_df.pivot_table(index='reviewerID', columns='asin', values='rating')
# print(user_games_df.head())

# lets see how big the data will be: the row will be the reviewerID and the columns will be asin
