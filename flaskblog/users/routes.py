from flask import flash, redirect, render_template, request, url_for, Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (LoginForm, RegistrationForm, UpdateAccountForm,
                                   RequestPasswordResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_image, send_reset_email

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', category='success')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('users/login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if request.method == 'POST' and form.validate():
        if form.image.data:
            saved_image = save_image(form.image.data)
            current_user.image = saved_image
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'users/profile_pics/{ current_user.image }')
    return render_template('users/account.html', title='My Account', image_file=image_file, form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestPasswordResetForm()
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/password_reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def password_reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Password reset token is invalid or expired.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if request.method == 'POST' and form.validate():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been changed. You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/password_reset.html', title='Reset Password', form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("users/user_posts.html", posts=posts, user=user)
