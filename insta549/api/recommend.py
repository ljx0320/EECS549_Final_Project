import flask
import insta549

@insta549.app.route('/api/', methods=['GET'])
def hello():
    return flask.jsonify("hello")

