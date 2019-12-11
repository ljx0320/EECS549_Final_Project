import numpy as np
import pandas as pd
import scipy
import sys
import json
import math
import random

from scipy.sparse.linalg import svds
from sklearn.model_selection import train_test_split


NUMBER_OF_FACTORS = 50
EVAL_RANDOM_SAMPLE_NON_INTERACTED_ITEMS = 100

# read in data
metadata_df = pd.read_json('data/filtered_meta_data.json')
rating_df = pd.read_json('data/test_processed_meta_data.json')


interactions_train_df, interaction_test_df = train_test_split(rating_df, test_size=0.20, random_state=42)
rating_indexed_df = rating_df.set_index('reviewerID')
interactions_indexed_test_df = interaction_test_df.set_index('reviewerID')
interactions_indexed_train_df = interactions_train_df.set_index('reviewerID')


def get_items_interacted(user_id, interactions_df):
    interacted_items = interactions_df.loc[user_id]['asin']
    # merged_items = pd.merge(metadata_df, interactions_df.loc[user_id][['asin', 'rating']], on='asin').sort_values('rating', ascending=False)
    # print(merged_items)
    return set(interacted_items)


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


class ModelEvaluator:
    def get_not_interacted_items_sample(self, person_id, sample_size, seed=42):
        interacted_items = get_items_interacted(person_id, rating_indexed_df)
        all_items = set(metadata_df['asin'])
        non_interacted_items = all_items - interacted_items

        random.seed(seed)
        non_interacted_items_sample = random.sample(non_interacted_items, sample_size)
        return set(non_interacted_items_sample)
    
    def _verify_hit_top_n(self, item_id, recommended_items, topn):
        try:
            index = next(i for i, c in enumerate(recommended_items) if c == item_id)
        except:
            index = -1
        hit = int(index in range(0, topn))
        return hit, index
    
    def evaluate_model_for_user(self, model, person_id):
        interacted_values_testset = interactions_indexed_test_df.loc[person_id]
        person_interacted_items_testset = set(interacted_values_testset['asin'])
        interacted_items_count_testset = len(person_interacted_items_testset)

        person_recs_df = model.recommend_items(person_id, items_to_ignore=get_items_interacted(person_id, interactions_indexed_train_df), topn=10000000000)
        hits_at_5_count = 0
        hits_at_10_count = 0

        for item_id in person_interacted_items_testset:
            non_interacted_items_sample = self.get_not_interacted_items_sample(person_id, sample_size=EVAL_RANDOM_SAMPLE_NON_INTERACTED_ITEMS, seed=random.randint(0, 2**32 - 1))
            items_to_filter_recs = non_interacted_items_sample.union(set([item_id]))
            valid_recs_df = person_recs_df[person_recs_df['asin'].isin(items_to_filter_recs)]
            valid_recs = valid_recs_df['asin'].values

            hit_at_5, index_at_5 = self._verify_hit_top_n(item_id, valid_recs, 5)
            hits_at_5_count += hit_at_5
            hit_at_10, index_at_10 = self._verify_hit_top_n(item_id, valid_recs, 10)
            hits_at_10_count += hit_at_10

        recall_at_5 = hits_at_5_count / float(interacted_items_count_testset)
        recall_at_10 = hits_at_10_count / float(interacted_items_count_testset)

        person_metrics = {
            'hits@5_count': hits_at_5_count,
            'hits@10_count': hits_at_10_count,
            'interacted_count': interacted_items_count_testset,
            'recall@5': recall_at_5,
            'recall@10': recall_at_10
        }

        return person_metrics

    def evaluate_model(self, model):
        people_metrics = []
        for idx, person_id in enumerate(list(interactions_indexed_test_df.index.unique().values)):
            if idx % 100 == 0:
                print('processed', idx, 'users')
            if person_id in set(interactions_indexed_train_df.index.values):
                person_metrics = self.evaluate_model_for_user(model, person_id)
                person_metrics['_person_id'] = person_id
                people_metrics.append(person_metrics)
        print('%d users processed' % idx)

        detailed_results_df = pd.DataFrame(people_metrics).sort_values('interacted_count', ascending=False)
        global_recall_at_5 = detailed_results_df['hits@5_count'].sum() / float(detailed_results_df['interacted_count'].sum())
        global_recall_at_10 = detailed_results_df['hits@10_count'].sum() / float(detailed_results_df['interacted_count'].sum())
 
        global_metrics = {
            'recall@5': global_recall_at_5,
            'recall@10': global_recall_at_10
        }

        return global_metrics, detailed_results_df

def main():
    model_evaluator = ModelEvaluator()
    # create pivot table
    users_items_pivot_matrix_df = interactions_train_df.pivot_table(index='reviewerID', columns='asin', values='rating', fill_value=0)

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

    # test_user = 'A1MRL66BXLXD1A'
    # print(cf_recommender_model.recommend_items(test_user, items_to_ignore=get_items_interacted(test_user, rating_df, metadata_df),verbose=True))
    print('Evaluating Collaborative Filtering model')
    cf_global_metrics, cf_detailed_results_df = model_evaluator.evaluate_model(cf_recommender_model)
    print('\nGlobal metrics:\n', cf_global_metrics)
    cf_detailed_results_df.head()
    

if __name__ == "__main__":
    main()

