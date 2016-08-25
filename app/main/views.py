from flask import render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required
from flask_moment import  datetime

from . import main
from .. import db
from .forms import ProfileForm, ProfileAdminForm, PostForm, PostAdminForm
from ..models import User, Role, Post, Permission, Language
from ..decorators import admin_required, permission_required


@main.route('/')
def index():
    pass


@main.route('/user/')
def user():
    users = User.query.order_by(User.last_seen.desc()).all()
    return render_template('user.html', users=users)


@main.route('user/profile/<username>/')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    if user is None:
        abort(404)
    else:
        return render_template('user_profile.html', user=user, posts=posts)


@main.route('/user/edit-profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
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


# TODO pagination
@main.route('/article/')
def article():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('article.html', posts=posts)


@main.route('/article/<int:id>/')
def user_article(id):
    posts = Post.query.filter_by(author_id=id).all()
    return render_template('user_article.html', posts=posts)


@main.route('/article/write/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def write_article():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        flash('Your article has been posted')
        return redirect(url_for('main.user_profile',
                                username=current_user.username))
    else:
        return render_template('write_article.html')


@main.route('/article/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    post = Post.query.get_or_404(id=id)
    form = PostForm()
    if current_user.id != post.author_id:
        abort(403)
    elif form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.timestamp = datetime.utcnow()
        db.session.add(post)
        flash('Your article has been update')
        return redirect(url_for('main.user_article', id=current_user.id))
    else:
        form.title.data = post.title
        form.body.data = post.body
        return render_template('edit_article.html', form=form, post=post)


@main.route('/manage/')
@login_required
@admin_required
def manage():
    pass


@main.route('/manage/user/<int:id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def user_manage(id):
    user = User.query.get_or_404(id)
    form = ProfileAdminForm(user)
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
        return render_template('user_manage.html', form=form, user=user)


@main.route('/manage/article/<int:id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def article_manage(id):
    post = Post.query.get_or_404(id)
    form = PostAdminForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = User.query.filter_by(id=form.author.data).first()
        post.body = form.body.data
        db.session.add(post)
        flash('update successfully')
        return redirect(url_for('main.manage'))
    else:
        form.title.data = post.title
        form.author.data = post.author_id
        form.body.data = post.body
        return render_template('article_manage.html', form=form)

