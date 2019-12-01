import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
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
ratings_df = pd.DataFrame(merged_df.groupby('title')['rating'].mean())
print(merged_df.head())
# but we also need to consider the number of ratings for each video game
ratings_df['number_of_ratings'] = merged_df.groupby('title')['rating'].count()
print(ratings_df.sort_values('number_of_ratings', ascending=True).iloc[25000])
print(ratings_df.sort_values('number_of_ratings', ascending=True).shape)
print(ratings_df.head(12))
ratings_df['rating'].hist(bins=50)
plt.show()
ratings_df['number_of_ratings'].hist(bins=60)
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
