import requests
from flask import Flask, json, Response
from flask_caching import Cache

from backend.src.constant import POSTS_URL, COMMENTS_URL, CACHE_TIMEOUT

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "redis",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 60 # default timeout
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


@app.route('/comments', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def comments():
    try:
        try:
            posts = requests.get(POSTS_URL)
        except requests.exceptions.RequestException as e:
            raise e
        try:
            comments = requests.get(COMMENTS_URL)
        except requests.exceptions.RequestException as e:
            raise e

        if posts.status_code != 200:
            return Response(
                response=json.dumps({'message': "Unable to fetch post, please check the url"}),
                status=400, mimetype='application/json'
            )
        post_data = posts.json()
        comment_data = comments.json()
        if not post_data:
            return Response(
                response=json.dumps({'message': "The is not post"}),
                status=400, mimetype='application/json'
            )
        organised_comments = organise_comments(post_data, comment_data)
        return Response(response=json.dumps(
            {"conversation ": organised_comments}), status=200)
    except Exception as e:
        return Response(
            response=json.dumps({'message': f"Error during comment parsing and error was {e}"}),
            status=400, mimetype='application/json'
        )


def organise_comments(posts, comments):
    sorted_comments = sorted(comments, key=lambda i: i['id'])
    for post in posts:
        comment_list = []
        for comment in sorted_comments:
            if post["id"] > comment["postId"]:
                continue
            elif post["id"] == comment["postId"]:
                comment_list.append(comment)
            else:
                break
        post["comments"] = comment_list
    return posts


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
