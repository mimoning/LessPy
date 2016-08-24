from flask_wtf import Form
from wtforms import StringField, SelectField, TextAreaField, SubmitField, \
    BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp

from ..models import Language, Role, User


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    main_language = SelectField('Main language', coerece=int)
    main_function = StringField('Main domain of development')
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.main_language.choices = [
            (language.id, language.name) for language in
            Language.query.order_by(Language.id).all()]


class EdiProfileAdminForm(Form):
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
        super(EdiProfileAdminForm, self).__init__(*args, **kwargs)
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


