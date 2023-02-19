from flask import Flask, request, jsonify
from flask.views import MethodView
from db import User, Announcement, Session
from schema import validate, CreatePost, CreateUser
from errors import HttpError
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

app = Flask('server')

bcrypt = Bcrypt(app)


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    http_response = jsonify({'status': 'error', 'description': error.message})
    http_response.status_code = error.status_code
    return http_response


@app.route('/users/all', methods=["GET"])
def get_users_all():
    with Session() as session:
        users = [{'id': p.id, 'username': p.username, 'users_email': p.users_email} for p in session.query(User).all()]
        return jsonify(users)


app.add_url_rule('/users/all', view_func=get_users_all)


@app.route('/posts/all', methods=["GET"])
def get_posts_all():
    with Session() as session:
        posts = [{'id': p.id,
                  'title': p.title,
                  'description': p.description,
                  'creation_date': p.creation_date,
                  'user_id': p.user_id} for p in session.query(Announcement).all()]
        return jsonify(posts)


app.add_url_rule('/posts/all', view_func=get_posts_all)


def get_user(user_id: int, session: Session):
    user = session.query(User).get(user_id)
    if user is None:
        raise HttpError(status_code=404, message='user not found')

    return user


class UserView(MethodView):
    def get(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
            return jsonify(
                {
                    'id': user.id,
                    'username': user.username,
                    'users_email': user.users_email
                }
            )

    def post(self):
        json_data = validate(CreateUser, request.json)
        json_data['password'] = bcrypt.generate_password_hash(json_data['password'].encode()).decode()
        with Session() as session:
            new_user = User(**json_data)
            session.add(new_user)
            try:
                session.commit()

            except IntegrityError:
                raise HttpError(status_code=409, message='user already exists')
            return jsonify(
                {
                    'id': new_user.id,
                    'username': new_user.username,
                    'password': new_user.password,
                    'users_email': new_user.users_email,
                }
            )

    def patch(self, user_id: int):
        json_data = validate(CreateUser, request.json)
        with Session() as session:
            user = get_user(user_id, session)
            for field, value in json_data.items():
                setattr(user, field, value)
            session.add(user)
            session.commit()
            return jsonify(
                {'status': 'success'}
            )

    def delete(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
            session.delete(user)
            session.commit()
            return jsonify(
                {'status': 'success'}
            )


def get_post(post_id: int, session: Session):
    advert = session.query(Announcement).get(post_id)
    if advert is None:
        raise HttpError(status_code=404, message='advert not found')

    return advert


class PostView(MethodView):
    def get(self, post_id: int):
        with Session() as session:
            post = get_post(post_id, session)
            return jsonify(
                {
                    'id': post.id,
                    'title': post.title,
                    'description': post.description,
                    'creation_date': post.creation_date,
                    'user_id': post.user_id
                }
            )

    def post(self):
        json_data = validate(CreatePost, request.json)
        with Session() as session:
            user = session.query(User.id).all()
            list_ = []
            for y in user:
                list_.append(int(y[0]))
            new_post = Announcement(**json_data)
            if new_post.user_id not in list_:
                return jsonify({"message": 'ads can only be posted by registered users'})
            session.add(new_post)
            session.commit()
            return jsonify(
                {
                    'id': new_post.id,
                    'title': new_post.title,
                    'description': new_post.description,
                    'creation_date': new_post.creation_date,
                    'user_id': new_post.user_id
                }
            )

    def patch(self, post_id, user_id):
        json_data = validate(CreatePost, request.json)
        with Session() as session:
            posts = get_post(post_id, session)
            if posts.user_id == user_id:
                for key, values in json_data.items():
                    setattr(posts, key, values)
                session.add(posts)
                session.commit()
                return jsonify({'status': 'success'})
            else:
                return jsonify({"message": 'ads can only be patched only owner'})

    def delete(self, post_id, user_id):
        with Session() as session:
            posts = get_post(post_id, session)
            if posts.user_id == user_id:
                session.delete(posts)
                session.commit()
                return jsonify({'status': 'success'})
            else:
                return jsonify({"message": 'ads can only be deleted only owner'})


app.add_url_rule('/users/<int:user_id>', view_func=UserView.as_view('users_id_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/users', view_func=UserView.as_view('users_id_post'), methods=['POST'])

app.add_url_rule('/posts/<int:post_id>/<int:user_id>', view_func=PostView.as_view('advert_id_patch'),
                 methods=['PATCH', 'DELETE'])
app.add_url_rule('/posts', view_func=PostView.as_view('advert_id_post'), methods=['POST'])
app.add_url_rule('/posts/<int:post_id>', view_func=PostView.as_view('advert_id_get'), methods=['GET'])
app.run(port=5001)
app.run(debug=True)
