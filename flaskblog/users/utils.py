import os
import secrets
from flask import current_app, url_for
from flask_mail import Message
from PIL import Image
from flaskblog import mail


def save_image(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    image_name = random_hex + file_ext
    image_path = os.path.join(current_app.root_path, 'static/profile_pics', image_name)
    new_size = (300, 300)
    resized_image = Image.open(form_picture)
    resized_image.thumbnail(new_size)
    resized_image.save(image_path)
    return image_name


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('FlaskBlog - Password Reset Request', sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.password_reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email.'''
    mail.send(msg)

