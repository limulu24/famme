from flask import Flask, render_template, request, flash, redirect
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Config

# 配置日志
if not os.path.exists('logs'):
    os.mkdir('logs')
    
file_handler = RotatingFileHandler('logs/famme.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

app = Flask(__name__)
app.config.from_object(Config)

# 速率限制
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["30 per minute"]
)

mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # 限制每IP每分钟最多5次提交
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        # 输入验证
        if not all([name, email, message]):
            flash('请填写所有必填项。', 'error')
            return render_template('index.html'), 400
            
        if len(message) > 1000:  # 限制留言长度
            flash('留言内容过长，请限制在1000字以内。', 'error')
            return render_template('index.html'), 400
            
        try:
            msg = Message(
                subject=f'新留言来自: {name}',
                sender=app.config['MAIL_USERNAME'],
                recipients=[app.config['ADMIN_EMAIL']],
                body=f'''
来自: {name}
邮箱: {email}
留言内容:
{message}
'''
            )
            mail.send(msg)
            logger.info(f'邮件发送成功给 {app.config["ADMIN_EMAIL"]}')
            flash('留言已成功发送！', 'success')
        except Exception as e:
            logger.error(f'发送邮件时出错: {str(e)}')
            flash('发送失败，请稍后重试。', 'error')
            return render_template('index.html'), 500
            
    return render_template('index.html')

# 错误处理
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    flash('请求过于频繁，请稍后再试。', 'error')
    return render_template('index.html'), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 