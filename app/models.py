from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_moment import datetime
from flask_login import UserMixin, AnonymousUserMixin

from . import db, login_manager


class Permission:
    WRITE_ARTICLES  = 0b00000001
    EDIT_ARTICLES   = 0b00000010
    WRITE_COMMENT   = 0b00000100
    DELETE_COMMENT  = 0b00001000
    DELETE_ARTICLES = 0b00010000
    ADMINISTER      = 0b11111111


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)
    permissions = db.Column(db.Integer())
    default = db.Column(db.Boolean(), default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def update_role():
        roles = {
            'Blocked user': (Permission.EDIT_ARTICLES, False),
            'User': (Permission.WRITE_ARTICLES |
                     Permission.EDIT_ARTICLES |
                     Permission.WRITE_COMMENT, True),
            'Moderator': (Permission.WRITE_ARTICLES |
                          Permission.EDIT_ARTICLES |
                          Permission.WRITE_COMMENT |
                          Permission.DELETE_COMMENT, False),
            'Administrator': (Permission.ADMINISTER, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.Permission = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

#TODO head portrait
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'))
    posts = db.relationship('posts', backref='author', lazy='dynamic')
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean(), default=False, index=True)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    main_language_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    main_function = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, property, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({str(property): self.id})

    def confirm(self, property, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get(property) != self.id:
            return False
        else:
            return True

    def confirm_user(self, token):
        if self.confirm('confirmed', token):
            self.confirmed = True
            db.session.add(self)
            return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False

    def is_administrator(self):
        return False


class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', backref='main_language', lazy='dynamic')

    @staticmethod
    def update_language():
        languages = [
            'C', 'C#', 'C++', 'Clojure', 'CoffeeScript', 'CSS', 'Go', 'Haskell',
            'HTML', 'Java', 'JavaScript', 'Lua', 'MatLab', 'Object-C', 'Perl',
            'PHP', 'Python', 'R', 'Ruby', 'Scala', 'Shell', 'Swift', 'Tex',
            'VimL'
        ]
        for i in languages:
            language = Language.query.filter_by(name=i).first()
            if language is None:
                language = Language(name=i)
                db.session.add(language)
        db.session.commit()



class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utc)
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))


class Comment(db.Model):
    pass


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
