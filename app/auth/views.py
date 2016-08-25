from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from ..email import send_mail


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_token('confirmed')
        send_mail(user.email, 'Confirm you account',
                  '/auth/email/confirm', user=user, token=token)
        flash('Welcome to join LessPy, a confirmation email has been sent to '
              'you by email, please confirm your account')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or
                                url_for('main.index'))
            else:
                flash('Invalid password')
        else:
            flash('Invalid username')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logout')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    elif current_user.confirm_user(token):
        flash('You have confirm your account')
        return redirect(url_for('main.index'))
    else:
        flash('The confirmation is invalid')
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed or current_user.is_anonymous:
        return redirect('main.index')
    else:
        return render_template('auth/unconfirmed')


@auth.before_app_request()
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth' \
                and request.endpoint != 'static':
            return redirect('auth.unconfirmed')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_token('confirmed')
    send_mail(current_user, 'Confirm you account',
              '/auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email, '
          'please confirm your account')
    return redirect(url_for('main.index'))


# TODO password change


# TODO forget password


# TODO email change


