from flask_wtf import Form
from wtforms import StringField, SelectField, TextAreaField, SubmitField, \
    BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp
from flask_pagedown.fields import PageDownField

from ..models import Language, Role, User


class ProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    main_language = SelectField('Main language', coerece=int)
    main_function = StringField('Main domain of development')
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.main_language.choices = [
            (language.id, language.name) for language in
            Language.query.order_by(Language.id).all()]


class ProfileAdminForm(Form):
    username = StringField('Username', validators=[
        DataRequired(), Length(0, 64), Regexp('^[A-Za-z][A-Za-z0-9._]*$', 0,
                                              'Username must have only letters,'
                                              'numbers, dots or underscores')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', coerce=int)
    confirmed = BooleanField('Confirmed')
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    main_language = SelectField('Main language', coerece=int)
    main_function = StringField('Main domain of development')
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(ProfileAdminForm, self).__init__(*args, **kwargs)
        self.main_language.choices = [
            (language.id, language.name) for language in
            Language.query.order_by(Language.id).all()]
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username \
                and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

    def validate_email(self, field):
        if field.data != self.user.email \
                and User.query.filter_by(email=field.email).first():
            raise ValidationError('Email already registered')


class PostForm(Form):
    title = StringField('Title', validators=[
        Length(0, 128), DataRequired('Your article must have a title')])
    body = PageDownField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PostAdminForm(Form):
    title = StringField('Title', validators=[
        Length(0, 128), DataRequired('Your article must have a title')])
    author = SelectField('author', coerce=int)
    body = PageDownField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(PostAdminForm, self).__init__(*args, **kwargs)
        self.author.choices = [(author.id, author.username) for author in
                               User.query.order_by(User.username.asc()).all()]


