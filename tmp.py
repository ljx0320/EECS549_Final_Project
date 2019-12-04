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

print(ratings_df.sort_values('number_of_ratings', ascending=False).head(20))
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

#user_games_df = merged_df.pivot_table(index='reviewerID', columns='asin', values='rating')
#print(user_games_df)
#print(user_games_df.shape)

user_games_df = merged_df.pivot_table(index='reviewerID', columns='asin', values='rating', fill_value=0)
print(user_games_df.shape)
print(user_games_df.head())

# now create a matrix including all users (row) and all games (column)
# user_games_df = merged_df.pivot_table(index='reviewerID', columns='asin', values='rating')
# print(user_games_df.head())
HALO_user_rating = user_games_df['B00005NZ1G']
FF_user_rating = user_games_df['B00005TNI6']
DIABLO_user_rating = user_games_df['B00178630A']

print(HALO_user_rating.head())
print(FF_user_rating.head())
similar_to_HALO = user_games_df.corrwith(HALO_user_rating)
similar_to_FF = user_games_df.corrwith(FF_user_rating)
similar_to_DIABLO = user_games_df.corrwith(DIABLO_user_rating)
print(similar_to_HALO.sort_values(ascending=False).head())
print(similar_to_FF.sort_values(ascending=False).head())
print(similar_to_DIABLO.sort_values(ascending=False).head())