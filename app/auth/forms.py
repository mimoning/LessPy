from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, Email

from ..models import User


class RegistrationForm(Form):
    username = StringField('Username', validators=[
        DataRequired(), Length(0, 64), Regexp('^[A-Za-z][A-Za-z0-9_.-]*$', 0,
                                              'Username must have only letters,'
                                              'numbers, dots or underscores')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo(password, 'password must be match')])
    submit = SubmitField('Submit')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')


