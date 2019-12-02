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
metadata_df.asin = metadata_df.asin.astype(object)
# read rating data
rating_df = pd.read_json('data/test_processed_meta_data.json')
# merge two data sets on asin
merged_df = pd.merge(metadata_df, rating_df, on='asin')
print(merged_df.head(10))
print(merged_df.shape)
# get the mean rating for every video game
ratings_df = pd.DataFrame(merged_df.groupby('asin')['rating'].mean())
users_df = pd.DataFrame(merged_df.groupby('reviewerID')['rating'].mean())
print(merged_df.head())
# but we also need to consider the number of ratings for each video game
ratings_df['number_of_ratings'] = merged_df.groupby('asin')['rating'].count()
users_df['number_of_ratings'] = merged_df.groupby('reviewerID')['rating'].count()

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
merged_df = merged_df.iloc[0:3]
user_games_df = merged_df.pivot_table(index='reviewerID', columns='asin', values='rating')
print(user_games_df)
user_games_df = merged_df.pivot_table(index='reviewerID', columns='asin', values='rating', fill_value=0)
print(user_games_df)
# now create a matrix including all users (row) and all games (column)
# user_games_df = merged_df.pivot_table(index='reviewerID', columns='asin', values='rating')
# print(user_games_df.head())