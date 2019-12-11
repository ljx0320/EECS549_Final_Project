import numpy as np
import pandas as pd
import scipy
import sys
import json
import math
import random

from scipy.sparse.linalg import svds


NUMBER_OF_FACTORS = 50
EVAL_RANDOM_SAMPLE_NON_INTERACTED_ITEMS = 100


def get_items_interacted(user_id, interactions_df, metadata_df):
    indexed_interactions_df = interactions_df.set_index('reviewerID')
    interacted_items = indexed_interactions_df.loc[user_id]['asin']
    merged_items = pd.merge(metadata_df, indexed_interactions_df.loc[user_id][['asin', 'rating']], on='asin').sort_values('rating', ascending=False)
    print(merged_items['title'].values.tolist())
    if merged_items.shape[0] >= 10:
        return ((merged_items['title'].values.tolist())[0:10], set(interacted_items))
    return (merged_items['title'].values.tolist(), set(interacted_items))


class CFRecommender:
    def __init__(self, cf_predictions_df, items_df=None):
        self.cf_predictions_df = cf_predictions_df
        self.items_df = items_df
    
    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        sorted_user_predictions = self.cf_predictions_df[user_id].sort_values(ascending=False).reset_index().rename(columns={user_id: 'pred_rating'})
        recommendations_df = sorted_user_predictions[~sorted_user_predictions['asin'].isin(items_to_ignore)].sort_values('pred_rating', ascending=False).head(topn)
        if verbose:
            if self.items_df is None:
                raise Exception('"item df" is required in verbose mode')
            recommendations_df = pd.merge(self.items_df, recommendations_df, on='asin')[['asin', 'pred_rating', 'title']].sort_values('pred_rating', ascending=False)
        
        return recommendations_df


def main():
    # read in data
    metadata_df = pd.read_json('data/filtered_meta_data.json')
    rating_df = pd.read_json('data/test_processed_meta_data.json')

    # create pivot table
    users_items_pivot_matrix_df = rating_df.pivot_table(index='reviewerID', columns='asin', values='rating', fill_value=0)

    # convert dataframe to matrix
    users_items_pivot_matrix = users_items_pivot_matrix_df.as_matrix()

    users_ids = list(users_items_pivot_matrix_df.index)

    # SVD
    U, sigma, Vt = svds(users_items_pivot_matrix, k = NUMBER_OF_FACTORS)
    sigma = np.diag(sigma)

    # reconstruct prediction matrix
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
    cf_preds_df = pd.DataFrame(all_user_predicted_ratings, columns = users_items_pivot_matrix_df.columns, index=users_ids).transpose()
    # initialize recommender model
    cf_recommender_model = CFRecommender(cf_preds_df, metadata_df)

    test_user = 'A1MRL66BXLXD1A'
    tmp, items_to_ignore = get_items_interacted(test_user, rating_df, metadata_df)
    print("tmp")
    print(tmp)
    print(cf_recommender_model.recommend_items(test_user, items_to_ignore=items_to_ignore, verbose=True))

if __name__ == "__main__":
    main()

