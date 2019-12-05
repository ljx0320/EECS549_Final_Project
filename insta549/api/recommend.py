import flask
import insta549

MODEL = insta549.app.config["MODEL"]
RATING_DF = insta549.app.config["RATING_DF"]
METADATA_DF = insta549.app.config["METADATA_DF"]


@insta549.app.route('/api/<string:userid>', methods=['GET'])
def recommend(userid):
    a = MODEL.recommend_items(userid, items_to_ignore=insta549.config.get_items_interacted(userid, RATING_DF, METADATA_DF),
                                         verbose=True).values.tolist()

    return flask.jsonify(a)