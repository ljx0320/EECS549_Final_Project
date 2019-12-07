import flask
import insta549

MODEL = insta549.app.config["MODEL"]
RATING_DF = insta549.app.config["RATING_DF"]
METADATA_DF = insta549.app.config["METADATA_DF"]
USER_GAMES_DF = insta549.app.config["USER_GAMES_DF"]
METADATA = insta549.app.config["METADATA"]

@insta549.app.route('/recommend/user/<string:userid>', methods=['GET'])
def recommend_user(userid):
    a = MODEL.recommend_items(userid, items_to_ignore=insta549.config.get_items_interacted(userid, RATING_DF, METADATA_DF),
                                         verbose=True).values.tolist()
    context = {}
    context['results'] = a
    context['userid'] = userid
    # return flask.jsonify(a)
    return flask.render_template("recommend_user.html", **context)

@insta549.app.route('/recommend/game/<string:asin>', methods=['GET'])
def recommend_game(asin):
    context = {}
    GAME_USER_RATING = USER_GAMES_DF[asin]
    results = USER_GAMES_DF.corrwith(GAME_USER_RATING).sort_values(ascending=False).iloc[1:10].index.tolist()
    context['asin'] = asin
    context['title'] = METADATA[asin]
    for i in range(len(results)):
        results[i] = METADATA[results[i]]
    context['results'] = results
    return flask.render_template("recommend_game.html", **context)
