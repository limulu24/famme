from flask import current_app
from flask_mail import Message
from app import mail

def send_message_email(data):
    msg = Message(
        subject=f'新留言来自: {data["name"]}',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[current_app.config['ADMIN_EMAIL']],
        body=f'''
来自: {data["name"]}
邮箱: {data["email"]}
留言内容:
{data["message"]}
'''
    )
    mail.send(msg) 