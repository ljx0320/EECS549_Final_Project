import os
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
import insta549

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'
NUMBER_OF_FACTORS = 50


class CFRecommender:
    def __init__(self, cf_predictions_df, items_df=None):
        self.cf_predictions_df = cf_predictions_df
        self.items_df = items_df

    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        sorted_user_predictions = self.cf_predictions_df[user_id].sort_values(ascending=False).reset_index().rename(
            columns={user_id: 'pred_rating'})
        recommendations_df = sorted_user_predictions[
            ~sorted_user_predictions['asin'].isin(items_to_ignore)].sort_values('pred_rating', ascending=False).head(
            topn)
        if verbose:
            if self.items_df is None:
                raise Exception('"item df" is required in verbose mode')
            recommendations_df = pd.merge(self.items_df, recommendations_df, on='asin')[
                ['asin', 'pred_rating', 'title']].sort_values('pred_rating', ascending=False)

        return recommendations_df

def get_items_interacted(user_id, interactions_df, metadata_df):
    indexed_interactions_df = interactions_df.set_index('reviewerID')
    interacted_items = indexed_interactions_df.loc[user_id]['asin']
    merged_items = pd.merge(metadata_df, indexed_interactions_df.loc[user_id][['asin', 'rating']], on='asin').sort_values('rating', ascending=False)
    print(merged_items)
    return set(interacted_items)


METADATA_DF = pd.read_json('/Users/lijiaxin/cs/EECS549/Project/insta549/data/filtered_meta_data.json')
RATING_DF = pd.read_json('/Users/lijiaxin/cs/EECS549/Project/insta549/data/test_processed_meta_data.json')

# create pivot table
users_items_pivot_matrix_df = RATING_DF.pivot_table(index='reviewerID', columns='asin', values='rating', fill_value=0)

# convert dataframe to matrix
users_items_pivot_matrix = users_items_pivot_matrix_df.as_matrix()

users_ids = list(users_items_pivot_matrix_df.index)

# SVD
U, sigma, Vt = svds(users_items_pivot_matrix, k=NUMBER_OF_FACTORS)
sigma = np.diag(sigma)

# reconstruct prediction matrix
all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
cf_preds_df = pd.DataFrame(all_user_predicted_ratings, columns=users_items_pivot_matrix_df.columns,
                           index=users_ids).transpose()

# initialize recommender model
MODEL = CFRecommender(cf_preds_df, METADATA_DF)

