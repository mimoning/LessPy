from flask import render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required

from . import main
from .. import db
from .forms import EditProfileForm, EdiProfileAdminForm
from ..models import User, Role, Post, Permission, Language
from ..decorators import admin_required


@main.route('/')
def index():
    pass


@main.route('user-profile/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    else:
        return render_template('user.html', user=user)


@main.route('edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.main_language = form.main_language.data
        current_user.main_function = form.main_function.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('main.user', username=current_user.username))
    else:
        form.name.data = current_user.name
        form.location.data = current_user.location
        form.main_language.data = current_user.main_language
        form.main_function.data = current_user.main_function
        form.about_me.data = current_user.about_me
        return render_template('edit_profile.html', form=form)


@main.route('user-management/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_management(id):
    user = User.query.get_or_404(id)
    form = EdiProfileAdminForm(user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = Role.query.get_or_404(form.role.data)
        user.confirm = form.confirmed.data
        user.name = form.name.data
        user.location = form.location.data
        user.main_language = Language.query.get(form.main_language.data)
        user.main_function = form.main_function.data
        user.about_me = form.about_me.data
        flash('update successfully')
        return redirect(url_for('main.index'))
    else:
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role_id
        form.confirmed.data = user.confirm
        form.name.data = user.name
        form.location.data = user.location
        form.main_language.data = user.main_language_id
        form.main_function.data = user.main_function
        form.about_me.data = user.about_me
        return render_template('user_management.html', form=form, user=user)



